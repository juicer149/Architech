# =============================================================================
# architech/codex/runtime/context.py
# =============================================================================
"""
ExecutionContext — coordination of deferred Output effects.

One ExecutionContext exists per Codex execution (descriptor call).

Responsibilities
----------------
- Collect PHASE-timed Output effects
- Apply CLUSTER-timed effects immediately
- Flush deferred effects in deterministic order

Flush order
-----------
1. CUSTOM effects (must never abort execution)
2. INHERENT effects (may raise)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List

from ..ir.effect import Effect
from ..ir.output import Output
from ..ir.timing import Timing


@dataclass(slots=True)
class _DeferredEffect:
    out: Output
    value: Any
    instance: Any
    field_name: str
    apply: Callable[[Output, Any, Any, str], Any]


class ExecutionContext:
    __slots__ = ("_queue",)

    def __init__(self) -> None:
        self._queue: List[_DeferredEffect] = []

    # ------------------------------------------------------------------

    def record(
        self,
        *,
        out: Output,
        value: Any,
        instance: Any,
        field_name: str,
        apply: Callable[[Output, Any, Any, str], Any],
    ) -> Any:
        if not out.enabled or out.effect is Effect.DROP:
            return None

        if out.timing is Timing.CLUSTER:
            return apply(out, value, instance, field_name)

        self._queue.append(
            _DeferredEffect(out, value, instance, field_name, apply)
        )
        return None

    # ------------------------------------------------------------------

    def flush(self) -> None:
        if not self._queue:
            return

        # CUSTOM first
        for rec in self._queue:
            if rec.out.effect is Effect.CUSTOM:
                rec.apply(rec.out, rec.value, rec.instance, rec.field_name)

        # INHERENT last
        for rec in self._queue:
            if rec.out.effect is Effect.INHERENT:
                rec.apply(rec.out, rec.value, rec.instance, rec.field_name)

        self._queue.clear()
