# ================================================================
# Architech/codex/engine.py
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
from typing import List, Optional

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

    __slots__ = ("phase_q", "codex_q", "strict")

    def __init__(self, strict: bool):
        self.strict = strict
        self.phase_q: List[Violation] = []
        self.codex_q: List[Violation] = []

    @staticmethod
    def _flush(queue: List[Violation]):
        if not queue:
            return

        # kanske skapa en funktion som är just läsa Praxis, dvs detta skulle kunna göras via 
        # bit operation att bara matcha Praxis.action och Praxis.timing via en matris
        # för att enkelt kunna ändra logik på rätt ställe om man ändrar Praxis definitionen?
        to_print = []
        to_raise = []

        # branchless-ish split
        for v in queue:
            act = v.principle.praxis.action
            if act is False:
                to_print.append(v)
            elif act is True:
                to_raise.append(v)

        # print first
        for v in to_print:
            print(
                f"[{v.principle.label}] {v.error} "
                f"(phase={v.phase.name}, section={v.section}, cluster={v.cluster})"
            )

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
        self._flush(self.phase_q)
        self.phase_q.clear()

    def flush_codex(self):
        self._flush(self.codex_q)
        self.codex_q.clear()


# -------------------------------------------------------------------
# CodexEngine
# -------------------------------------------------------------------
class CodexEngine:
    """
    Executes CodexSpec using strict-first logic.
    """

    __slots__ = ("spec", "strict")

    def __init__(self, spec: CodexSpec, config: CodexConfig):
        self.spec = spec
        self.strict = self._resolve_strict(config.strict)

    # --------------------------------------------------------------
    # Strict-mode detection
    # --------------------------------------------------------------

    def _resolve_strict(self, user_flag: Optional[bool]) -> bool:
        if user_flag is not None:
            return user_flag

        # auto mode: semantic iff ANY principle exists
        for ps in self.spec.phases.values():
            for s in ps.sections:
                if s.principle is not None:
                    return False
        return True

    # --------------------------------------------------------------
    # Phase executor
    # --------------------------------------------------------------

    def run_phase(self, phase: Phase, value):
        p = self.spec.phases.get(phase)
        if not p:
            return value

        ctx = ExecutionContext(self.strict)
        current = value

        for i, sec in enumerate(p.sections):
            current = self._run_section(sec, phase, i, current, ctx)

        ctx.flush_phase()
        ctx.flush_codex()
        return current

    # --------------------------------------------------------------
    # Section executor
    # --------------------------------------------------------------

    def _run_section(self, section: SectionSpec, phase: Phase, sec_idx: int, value, ctx: ExecutionContext):
        if self.strict:
            return self._run_section_strict(section, value)

        # semantic mode strict-first
        # detta hade med kunnat ändras för en snabb kontroll av att man skapar ett exception och
        # bara jämnför mot, dvs; if result is type(Exception): ...? är inte det snabbare?
        try:
            return self._run_section_strict(section, value)
        except BaseException:
            return self._run_section_semantic(section, phase, sec_idx, value, ctx)

    # --------------------------------------------------------------
    # STRICT MODE — hyper-optimized
    # --------------------------------------------------------------

    def _run_section_strict(self, section: SectionSpec, value):
        current = value
        _run_cluster = self._run_cluster_strict

        for cluster in section.clusters:
            current = _run_cluster(cluster, current)

        return current

    def _run_cluster_strict(self, cluster: ClusterSpec, value):
        """
        Optimized fallback cascade.

        Fast path: no fallbacks
        Slow path: fallback probing + retry primary
        """
        current = value

        primary = cluster.primary
        fallbacks = cluster.fallbacks
        fb_len = len(fallbacks)

        # --- FAST PATH (NO FALLBACKS) ------------------------------------
        if fb_len == 0:
            out = primary(current)

            if out is None:
                return current

            if isinstance(out, BaseException):
                raise out

            return out

        # --- FALLBACK PATH ------------------------------------------------
        out = primary(current)

        if isinstance(out, BaseException):
            # try fallbacks one by one
            for fb in fallbacks:
                nxt = fb(current)

                if not isinstance(nxt, BaseException):
                    # fallback success → retry primary
                    out = primary(nxt)

                    if not isinstance(out, BaseException):
                        return out if out is not None else nxt

            # no fallback could fix it
            raise out

        # success from primary
        return out if out is not None else current

    # --------------------------------------------------------------
    # SEMANTIC REPLAY
    # --------------------------------------------------------------

    def _run_section_semantic(
        self,
        section: SectionSpec,
        phase: Phase,
        sec_idx: int,
        value,
        ctx: ExecutionContext,
    ):
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
        value,
        principle: Principle,
        ctx: ExecutionContext,
    ):
        current = value
        last_exc = None

        primary = cluster.primary
        fallbacks = cluster.fallbacks

        # --- try primary + fallbacks -------------------------------------
        try_fns = (primary, *fallbacks)

        for fn in try_fns:
            try:
                out = fn(current)
            except Exception as hard:
                raise hard

            if isinstance(out, BaseException):
                last_exc = out
                continue

            # success
            return out if out is not None else current

        # --- fail → semantic violation -----------------------------------
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
