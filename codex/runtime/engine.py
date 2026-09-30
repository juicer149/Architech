# =============================================================================
# architech/codex/runtime/engine.py
# =============================================================================
"""
Engine — strict-first executor for Codex pipelines.

Responsibility
--------------
Engine is the *mechanical executor* of compiled pipelines.

It:
- executes Nodes sequentially
- supports PRIMARY / FALLBACK / OR semantics
- distinguishes strict vs semantic execution

Engine does NOT:
- know about descriptors
- know about Output, Effect, or Timing
- perform any side effects

Contract
--------
Engine.run(pipeline, value) -> (result, is_exception)

- result:
    Final value OR the last exception object produced.
- is_exception:
    True if result should be routed through exception Output.
"""

from __future__ import annotations

from typing import Any, Iterable, Protocol, Tuple

from ..ir.node import Node


class PipelineLike(Protocol):
    """
    Duck-typed pipeline contract.
    """
    @property
    def nodes(self) -> Iterable[Node]:
        ...


class Engine:
    def run(self, pipeline: PipelineLike, value: Any) -> Tuple[Any, bool]:
        ok, strict_out = self._try_strict(pipeline, value)
        if ok:
            return strict_out, False

        sem_value, last_exc = self._run_semantic(pipeline, value)
        if last_exc is not None:
            return last_exc, True
        return sem_value, False

    # ------------------------------------------------------------------
    # Strict execution
    # ------------------------------------------------------------------

    def _try_strict(self, pipeline: PipelineLike, value: Any) -> Tuple[bool, Any]:
        current = value
        try:
            for node in pipeline.nodes:
                current = self._run_node_strict(node, current)
            return True, current
        except BaseException as exc:
            return False, exc

    def _run_node_strict(self, node: Node, current: Any) -> Any:
        primary = node.fn
        fallbacks = node.fallbacks
        ors = node.ors

        last_exc: BaseException | None = None

        if not fallbacks and not ors:
            out = primary(current)
            if out is None:
                return current
            if isinstance(out, BaseException):
                raise out
            return out

        if fallbacks:
            out = primary(current)
            if not isinstance(out, BaseException):
                return current if out is None else out

            last_exc = out
            for fb in fallbacks:
                fixed = fb(current)
                if isinstance(fixed, BaseException):
                    last_exc = fixed
                    continue

                out2 = primary(fixed)
                if isinstance(out2, BaseException):
                    last_exc = out2
                    continue

                return fixed if out2 is None else out2

            raise last_exc  # type: ignore[arg-type]

        for fn in (primary, *ors):
            out = fn(current)
            if out is None:
                return current
            if isinstance(out, BaseException):
                last_exc = out
                continue
            return out

        if last_exc is not None:
            raise last_exc
        return current

    # ------------------------------------------------------------------
    # Semantic replay
    # ------------------------------------------------------------------

    def _run_semantic(
        self, pipeline: PipelineLike, value: Any
    ) -> Tuple[Any, BaseException | None]:
        current = value
        last_exc: BaseException | None = None

        for node in pipeline.nodes:
            current, err = self._run_node_semantic(node, current)
            if err is not None:
                last_exc = err

        return current, last_exc

    def _run_node_semantic(
        self, node: Node, current: Any
    ) -> Tuple[Any, BaseException | None]:
        primary = node.fn
        fallbacks = node.fallbacks
        ors = node.ors

        last_exc: BaseException | None = None

        try:
            out = primary(current)
        except BaseException as hard:
            last_exc = hard
        else:
            if not isinstance(out, BaseException):
                return (current if out is None else out), None
            last_exc = out

        for fb in fallbacks:
            try:
                fixed = fb(current)
            except BaseException as e_fb:
                last_exc = e_fb
                continue

            if isinstance(fixed, BaseException):
                last_exc = fixed
                continue

            try:
                out2 = primary(fixed)
            except BaseException as e_pr:
                last_exc = e_pr
                continue

            if isinstance(out2, BaseException):
                last_exc = out2
                continue

            return (fixed if out2 is None else out2), None

        for alt in ors:
            try:
                out_alt = alt(current)
            except BaseException as e_alt:
                last_exc = e_alt
                continue

            if isinstance(out_alt, BaseException):
                last_exc = out_alt
                continue

            return (current if out_alt is None else out_alt), None

        return current, last_exc
