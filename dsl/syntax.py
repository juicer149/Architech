# ================================================================
# architech/dsl/syntax.py
# ================================================================
"""
StepChain — fluent DSL builder for SectionNode.

This class builds up an abstract pipeline like:

    SET >> f1 << fb1 << fb2 >> f2 | semantic_token

The DSL itself is semantics-free:
- No exceptions, no validation rules
- No Principle/Praxis logic
- No execution concerns

Backends (Codex, or others) map SectionNode into their own IR.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List

from .nodes import StepNode, ClusterNode, SectionNode
from .phase_token import PhaseTokenBase
from .protocol import StepFn


@dataclass
class StepChain:
    phase_token: PhaseTokenBase
    _clusters: List[ClusterNode] = field(default_factory=list)
    _semantic: Any | None = None

    def __init__(self, phase_token: PhaseTokenBase, first: StepFn):
        self.phase_token = phase_token
        self._clusters = [ClusterNode(primary=StepNode(first), fallbacks=())]
        self._semantic = None

    def __rshift__(self, fn: StepFn) -> "StepChain":
        self._clusters.append(ClusterNode(primary=StepNode(fn), fallbacks=()))
        return self

    def __lshift__(self, fn: StepFn) -> "StepChain":
        if not self._clusters:
            raise ValueError("Cannot add fallback without a primary step.")
        last = self._clusters[-1]
        self._clusters[-1] = ClusterNode(
            primary=last.primary,
            fallbacks=last.fallbacks + (StepNode(fn),),
        )
        return self

    def __or__(self, semantic: Any) -> "StepChain":
        # denna ska ändras mot att tillåta or statements mellan steps
        # dvs att man kan skriva: SET >> f1 | f2 @ ERROR, där det då betyder 
        # antingen f1 eller f2. Nuvarande or ska ändras att överlagra "@" 
        # istället
        self._semantic = semantic
        return self


    # def __matmul__(self, other: Any) -> "StepChain":
    #     """Overload "@" operator to set semantic metadata."""
    #     self._semantic = semantic 
    #     return self


    def to_section(self) -> SectionNode:
        """Materialize to an immutable SectionNode."""
        return SectionNode(
            phase=self.phase_token.key,
            clusters=tuple(self._clusters),
            semantic=self._semantic,
        )

    def __repr__(self) -> str:
        return (f"StepChain(phase={self.phase_token.key!r}, "
                f"clusters={self._clusters!r}, semantic={self._semantic!r})")

# kanske tom att man skulle särskilja mellan de som agerar på section level och 
# step level, dvs att <<, | som tillhör en cluster/sequence och sedan att 
# >> och @ tillhör section level?
# men att dem kan kombineras i fasad som ex då codex använder
# detta skulle ge något osm SequenceChain och SectionChain, där linear:bool skulle 
# bo i SectionChain?
