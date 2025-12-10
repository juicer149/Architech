# ================================================================
# architech/codex/semantics.py
# ================================================================
"""
Semantic vocabulary for Codex.

Responsibility
--------------
Defines the *meaning* attached to validation/transform steps:

    • Praxis    → timing (when) + action (how)
    • Principle → label + praxis + optional exception type

This module is pure semantic data. No descriptor or engine logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Type, Any


@dataclass(frozen=True, slots=True)
class Praxis:
    """
    Minimal semantic control flags.

    timing:
        True  → cluster-level (immediate flush)
        False → phase-level  (flushed at end of Phase)
        None  → codex-level  (flushed after entire Codex)

    action:
        True  → raise exception
        False → print violation
        None  → ignore violation
    """

    timing: bool | None = None
    action: bool | None = None


@dataclass(frozen=True, slots=True)
class Principle:
    """
    A semantic principle.

    Attributes
    ----------
    label:
        Human-readable semantic label ("error", "warn", ...)

    praxis:
        Controls when/how violations are realized.

    exc_type:
        Exception type used when action=True (raise).
    """

    label: str
    praxis: Praxis
    exc_type: Optional[Type[BaseException]] = None

    def effective_exc_type(self) -> Type[BaseException]:
        """
        Return the effective exception type for this principle.
        """
        return self.exc_type or RuntimeError


def normalize_principle(obj: Any) -> Optional[Principle]:
    """
    Normalize semantic tokens coming from the DSL:

        None       → None
        Principle  → itself
        str        → Principle(label=str, praxis=DEFAULT_PRAXIS)

    The actual DEFAULT_PRAXIS is defined in codex.constants.
    To avoid circular imports, we import lazily when needed.
    """
    if obj is None:
        return None
    if isinstance(obj, Principle):
        return obj
    if isinstance(obj, str):
        # Lazy import to break circular dependency.
        from .constants import DEFAULT_PRAXIS  # type: ignore

        return Principle(obj, DEFAULT_PRAXIS)
    raise TypeError(f"Cannot normalize semantic token {obj!r}")
