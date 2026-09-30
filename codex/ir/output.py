# =============================================================================
# architech/codex/ir/output.py
# =============================================================================
"""
Output — routing policy for values and exceptions.

An Output describes *what should happen* to a value or exception
after pipeline execution.

This module is IR-only:
- no side effects
- no writes
- no raises
- no logging

Core ideas
----------
- Effect describes WHAT happens
- Timing describes WHEN it happens
- Runtime owns HOW it happens

Important invariants
--------------------
- There is no legacy destination system.
- There is exactly one semantic path.
- INHERENT behavior is implemented in runtime code, not data.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Tuple, Union

from .effect import Effect
from .timing import Timing

TypeFilter = Union[type, Tuple[type, ...], None, bool]


def normalize_type_filter(tf: TypeFilter) -> Optional[Tuple[type, ...]]:
    if tf is None or tf is False:
        return None
    if isinstance(tf, type):
        return (tf,)
    if isinstance(tf, tuple) and all(isinstance(t, type) for t in tf):
        return tf
    raise TypeError(f"Invalid type_filter: {tf!r}")


@dataclass(slots=True)
class Output:
    """
    Declarative routing policy for a pipeline result.

    Fields
    ------
    label:
        Optional semantic label (error, warning, info, custom).
        Used for logging, tracing, aggregation, hooks.

    is_exception:
        True if this Output applies to exception results.

    enabled:
        Whether this output channel is active.

    effect:
        WHAT should happen (INHERENT / CUSTOM / DROP).

    timing:
        WHEN it should happen (IMMEDIATE / PHASE / CODEX).

    hook:
        Required when effect == CUSTOM.
        Signature: hook(value_or_exc, instance, field_name)

    type_filter:
        Optional runtime type validation for values.

    default / use_default:
        Optional soft-fallback mechanism.
    """
    is_exception: bool = False
    enabled: bool = True

    label: str | None = None
    effect: Effect = Effect.INHERENT
    timing: Timing = Timing.IMMEDIATE

    hook: Optional[Callable[[Any, Any, str], Any]] = None

    type_filter: TypeFilter = None
    default: Any = None
    use_default: bool = False

    @property
    def normalized_type_filter(self) -> Optional[Tuple[type, ...]]:
        return normalize_type_filter(self.type_filter)

    @property
    def allows_fallback(self) -> bool:
        return bool(self.use_default)

    def validate(self) -> None:
        """
        Validate internal invariants.

        Called by runtime during configuration build.
        """
        if self.effect is Effect.CUSTOM and self.hook is None:
            raise ValueError("CUSTOM effect requires hook")
        if self.effect is not Effect.CUSTOM and self.hook is not None:
            raise ValueError("hook is only allowed with CUSTOM effect")
