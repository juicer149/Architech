# ================================================================
# architech/codex/engine.py
# ================================================================
"""
CodexEngine — strict-first deterministic executor.

STRICT MODE
-----------
Pure Python execution. No semantics, no queues.
If a step returns an Exception → raise it immediately.

SEMANTIC MODE
-------------
1. Try strict section
2. If failure → semantic replay
3. Violations added to queues according to Praxis.timing:
       True  → cluster-level (immediate)
       False → phase-level
       None  → codex-level
4. Queues flushed deterministically

This engine has *zero overhead* in strict-mode beyond Python calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Any, Callable

from .models import (
    Phase,
    ClusterSpec,
    SectionSpec,
    CodexSpec,
    CodexConfig,
)
from .constants import DEFAULT_PRAXIS
from .semantics import Principle


# -------------------------------------------------------------------
# Violation record
# -------------------------------------------------------------------

@dataclass(slots=True)
class Violation:
    principle: Principle
    error: BaseException
    phase: Phase
    section: int
    cluster: int


# -------------------------------------------------------------------
# ExecutionContext
# -------------------------------------------------------------------

class ExecutionContext:
    """
    Aggregates semantic violations according to Praxis.timing.
    """

    __slots__ = ("phase_q", "codex_q", "strict", "logger")

    def __init__(self, strict: bool, logger: Optional[Callable[[str], None]] = None):
        """
        Execution context for semantic replay.

        Parameters
        - strict: Whether the engine is in strict mode.
        - logger: Optional callable used for informational output during
                  violation flushing. When None, falls back to `print`.
        """
        self.strict = strict
        self.logger = logger
        self.phase_q: List[Violation] = []
        self.codex_q: List[Violation] = []

    @staticmethod
    def _flush(queue: List[Violation], logger: Optional[Callable[[str], None]] = None):
        if not queue:
            return

        to_print: List[Violation] = []
        to_raise: List[Violation] = []

        for v in queue:
            act = v.principle.praxis.action
            if act is False:
                to_print.append(v)
            elif act is True:
                to_raise.append(v)

        # print first
        for v in to_print:
            msg = (
                f"[{v.principle.label}] {v.error} "
                f"(phase={v.phase.name}, section={v.section}, cluster={v.cluster})"
            )
            if logger is not None:
                logger(msg)
            else:
                print(msg)

        # raise last
        if to_raise:
            exc_type = to_raise[0].principle.effective_exc_type()
            msg = "\n".join(
                f"[{v.principle.label}] {v.error} "
                f"(phase={v.phase.name}, section={v.section}, cluster={v.cluster})"
                for v in to_raise
            )
            raise exc_type(msg)

        queue.clear()

    def flush_phase(self):
        self._flush(self.phase_q, self.logger)
        self.phase_q.clear()

    def flush_codex(self):
        self._flush(self.codex_q, self.logger)
        self.codex_q.clear()


# -------------------------------------------------------------------
# CodexEngine
# -------------------------------------------------------------------

class CodexEngine:
    """
    Executes CodexSpec using strict-first logic.
    """

    __slots__ = ("spec", "strict", "logger")

    def __init__(self, spec: CodexSpec, config: CodexConfig):
        self.spec = spec
        self.strict = self._resolve_strict(config.strict)
        # pass logger down to ExecutionContext
        self.logger = getattr(config, "logger", None)

    # --------------------------------------------------------------
    # Strict-mode detection
    # --------------------------------------------------------------

    def _resolve_strict(self, user_flag: Optional[bool]) -> bool:
        if user_flag is not None:
            return user_flag
        # Auto mode: semantic iff ANY principle exists (O(1) via IR flag)
        return not self.spec.has_principles

    # --------------------------------------------------------------
    # Phase executor
    # --------------------------------------------------------------

    def run_phase(self, phase: Phase, value: Any) -> Any:
        """
        Run all sections for the given phase on `value`.
        """
        p = self.spec.phases.get(phase)
        if not p:
            return value

        ctx = ExecutionContext(self.strict, self.logger)
        current = value

        for i, sec in enumerate(p.sections):
            current = self._run_section(sec, phase, i, current, ctx)

        ctx.flush_phase()
        ctx.flush_codex()
        return current

    # --------------------------------------------------------------
    # Section executor
    # --------------------------------------------------------------

    def _run_section(
        self,
        section: SectionSpec,
        phase: Phase,
        sec_idx: int,
        value: Any,
        ctx: ExecutionContext,
    ) -> Any:
        if self.strict:
            return self._run_section_strict(section, value)

        # Semantic mode: probe strict once without propagating exception,
        # then semantic replay only on failure.
        res, err = self._try_section_strict(section, value)
        if err is None:
            return res
        return self._run_section_semantic(section, phase, sec_idx, value, ctx)

    # --------------------------------------------------------------
    # STRICT MODE — hyper-optimized
    # --------------------------------------------------------------

    def _run_section_strict(self, section: SectionSpec, value: Any) -> Any:
        current = value
        for cluster in section.clusters:
            current = self._run_cluster_strict(cluster, current)
        return current

    def _try_section_strict(self, section: SectionSpec, value: Any) -> tuple[Any, Optional[BaseException]]:
        """
        Strict probe that returns (result, error) without raising.

        Used by semantic mode to avoid expensive raise/catch in the hot path.
        """
        current = value
        try:
            for cluster in section.clusters:
                current = self._run_cluster_strict(cluster, current)
            return current, None
        except BaseException as e:
            return current, e

    def _run_cluster_strict(self, cluster: ClusterSpec, value: Any) -> Any:
        """
        Optimized execution for a single cluster.

        Cases:
            - primary only
            - primary + fallbacks
            - primary + OR alternatives
        """
        primary = cluster.primary
        fallbacks = cluster.fallbacks
        ors = cluster.ors

        # Ensure we never silently mix fallbacks and ors.
        if fallbacks and ors:
            raise RuntimeError(
                "ClusterSpec has both fallbacks and ors; "
                "this should not be possible under DSL invariants."
            )

        current = value

        # --- primary only --------------------------------------------------
        if not fallbacks and not ors:
            out = primary(current)

            if out is None:
                return current

            if isinstance(out, BaseException):
                raise out

            return out

        # --- primary + fallbacks -------------------------------------------
        if fallbacks:
            out = primary(current)

            if not isinstance(out, BaseException):
                # success
                return current if out is None else out

            last_exc: BaseException = out
            # try fallbacks one by one
            for fb in fallbacks:
                fixed = fb(current)

                if isinstance(fixed, BaseException):
                    last_exc = fixed
                    continue

                # fallback success → retry primary with fixed value
                out2 = primary(fixed)

                if isinstance(out2, BaseException):
                    last_exc = out2
                    continue

                # New semantics: if primary returns None after fallback,
                # keep the fallback output (fixed) rather than original current.
                return fixed if out2 is None else out2

            # no fallback could fix it
            raise last_exc

        # --- primary + OR alternatives -------------------------------------
        assert ors

        last_exc: BaseException | None = None

        for fn in (primary, *ors):
            out = fn(current)

            if out is None:
                # treat None as “no change but success”
                return current
            if isinstance(out, BaseException):
                last_exc = out
                continue

            # success
            return out

        # all failed
        if last_exc is None:
            # extremely unlikely: no fn produced an Exception OR a value
            # (e.g. fn never returned)
            return current

        raise last_exc

    # --------------------------------------------------------------
    # SEMANTIC REPLAY
    # --------------------------------------------------------------

    def _run_section_semantic(
        self,
        section: SectionSpec,
        phase: Phase,
        sec_idx: int,
        value: Any,
        ctx: ExecutionContext,
    ) -> Any:
        current = value
        principle = section.principle or Principle("codex", DEFAULT_PRAXIS)

        for c_idx, cluster in enumerate(section.clusters):
            current = self._run_cluster_semantic(
                cluster, phase, sec_idx, c_idx, current, principle, ctx
            )
        return current

    def _run_cluster_semantic(
        self,
        cluster: ClusterSpec,
        phase: Phase,
        sec_idx: int,
        c_idx: int,
        value: Any,
        principle: Principle,
        ctx: ExecutionContext,
    ) -> Any:
        """
        Semantic execution for a cluster.

        We treat all available steps (primary, fallbacks, ors) as
        potential “repair” or alternative paths. First success wins.

        If all fail → semantic violation is recorded according to
        Principle.praxis.timing.
        """
        current = value
        last_exc: BaseException | None = None

        # Flatten all possible candidates
        fns = (cluster.primary, *cluster.fallbacks, *cluster.ors)

        for fn in fns:
            try:
                out = fn(current)
            except Exception as hard:
                # hard errors are not wrapped; surfaced immediately
                raise hard

            if isinstance(out, BaseException):
                last_exc = out
                continue

            # success
            return current if out is None else out

        # --- fail → semantic violation -------------------------------------
        if last_exc is None:
            return current

        timing = principle.praxis.timing
        record = Violation(principle, last_exc, phase, sec_idx, c_idx)

        if timing is True:
            ExecutionContext._flush([record])
        elif timing is False:
            ctx.phase_q.append(record)
        else:
            ctx.codex_q.append(record)

        return current
