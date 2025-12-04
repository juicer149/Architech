# ================================================================
# blueprint/dsl/nodes.py
# ================================================================
"""
Pure structural DSL nodes independent of Codex runtime.

These nodes are consumed by the backend (Codex) to create AST/IR models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple


@dataclass(frozen=True, slots=True)
class StepNode:
    """
    DSL-level representation of a single step.

    primary:
        True  → primary step in the Section
        False → fallback step attached to the most recent primary

    fn:
        Raw callable-like object (backend decides how to execute it).
    """

    primary: bool
    fn: Any


@dataclass(frozen=True, slots=True)
class SectionNode:
    """
    A DSL-level section: a list of StepNode plus an optional semantic token.

    At this layer the semantic token is *opaque* (backend interprets it).
    """

    steps: Tuple[StepNode, ...]
    semantic: Any | None
    phase_key: Any
    phase_kwargs: dict[str, Any]
