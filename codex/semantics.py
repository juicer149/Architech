# ================================================================
# Architech/codex/semantics.py
# ================================================================
"""
Semantic vocabulary for Codex.

Responsibility
--------------
Defines the *meaning* attached to validation/transform steps:
    • Praxis  → timing (when) + action (how)
    • Principle → label + praxis + optional exception type

This is pure semantic data. No execution logic and no Codex dependency.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Type

# fundrar även över denna filen, den heter semantics.py men kanske borde ändra namn
# till något som typ rules.py eller models.py eller något

@dataclass(frozen=True, slots=True)
class Praxis:
    """
    Minimal semantic control:

    timing:
        True  → cluster-level (immediate flush)
        False → phase-level  (flushed at end of Phase)
        None  → codex-level  (flushed after entire Codex)

    action:
        True  → raise exception
        False → print violation
        None  → ignore violation
    """
    # båda dessa borde vara = DEFAULT_TIMING och = DEFAULT_ACTION
    # dessa båda ska bo i constants.py
    timing: bool | None = None
    action: bool | None = None


@dataclass(frozen=True, slots=True)
class Principle:
    """
    A semantic principle:

    Attributes
    ----------
    label:
        Human-readable semantic label ("error", "warn", ...)

    praxis:
        Controls when/how violations are realized.

    exc_type:
        Exception type used when action=True (raise).
    """
    # även dessa borde ha defaults från constants.py
    label: str
    praxis: Praxis  # skulle kunna vara = Praxis() då via att den har default där
    exc_type: Optional[Type[BaseException]] = None  # ett default exception

    def effective_exc_type(self) -> Type[BaseException]:
        return self.exc_type or RuntimeError


def normalize_principle(obj):
    """
    Normalize semantic tokens coming from DSL:
        None       → None
        Principle  → itself
        str        → Principle(label=str, praxis=DEFAULT)
    """
    if obj is None:
        return None
    if isinstance(obj, Principle):
        return obj
    if isinstance(obj, str):
        return Principle(obj, Praxis())
    raise TypeError(f"Cannot normalize semantic token {obj!r}")
