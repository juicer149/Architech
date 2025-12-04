# ================================================================
# blueprint/dsl/syntax.py
# ================================================================
"""
StepChain — the pure symbolic DSL builder.

This DSL layer is intentionally:

    - stateless
    - context-free
    - semantics-free
    - backend-agnostic

Codex will later consume StepChain objects and convert them into
runtime phases, Section/Step IR, semantics bindings, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Tuple

from .nodes import StepNode, SectionNode
from .protocol import CallableLike, DSLPhaseKey


@dataclass(slots=True)
class StepChain:
    """
    Immutable symbolic builder representing a single DSL Section.

    Attributes
    ----------
    phase_key:
        Opaque phase identifier (Codex supplies actual meaning).

    phase_kwargs:
        Arbitrary config associated with the phase token.

    steps:
        List av (primary: bool, fn)

    semantic:
        Opaque semantic annotation — backend interprets it.
    """

    phase_key: DSLPhaseKey
    phase_kwargs: dict[str, Any]
    steps: List[Tuple[bool, CallableLike]] = field(default_factory=list)
    semantic: Any | None = None

    # ------------------------------------------------------------
    # Add primary fn
    # ------------------------------------------------------------
    def __rshift__(self, fn: CallableLike) -> "StepChain":
        return StepChain(
            self.phase_key,
            self.phase_kwargs,
            [*self.steps, (True, fn)],
            self.semantic,
        )

    # ------------------------------------------------------------
    # Add fallback fn
    # ------------------------------------------------------------
    def __lshift__(self, fn: CallableLike) -> "StepChain":
        return StepChain(
            self.phase_key,
            self.phase_kwargs,
            [*self.steps, (False, fn)],
            self.semantic,
        )

    # ------------------------------------------------------------
    # Add semantic token
    # ------------------------------------------------------------
    def __or__(self, token: Any) -> "StepChain":
        if self.semantic is not None:
            raise ValueError("Semantic token already attached.")
        return StepChain(
            self.phase_key,
            self.phase_kwargs,
            list(self.steps),
            token,
        )

    # ------------------------------------------------------------
    # Convert to SectionNode for backend consumption
    # ------------------------------------------------------------
    def to_node(self) -> SectionNode:
        return SectionNode(
            steps=tuple(StepNode(primary=primary, fn=fn) for primary, fn in self.steps),
            semantic=self.semantic,
            phase_key=self.phase_key,
            phase_kwargs=dict(self.phase_kwargs),
        )
