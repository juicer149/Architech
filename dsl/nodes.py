# ================================================================
# architech/dsl/nodes.py
# ================================================================
"""
Pure structural DSL nodes independent of any specific backend.

This module defines:

    - Relation: structural relation between tokens
    - StepToken: atomic pipeline element
    - Section: phase-specific collection of clusters

The DSL's job is purely structural:

    - It does not know what a “Principle” is.
    - It does not interpret semantic tokens.
    - It does not decide control flow or validation semantics.

Backends (such as Codex) consume these structures and map them to
their own IR and execution semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Tuple

from .protocol import DSLPhaseKey, Step


class Relation(Enum):
    """
    Structural relation of a token inside a cluster.

    PRIMARY
        The main token in the logical chain.

    FALLBACK
        A fallback alternative that is considered when some failure
        condition occurs for a PRIMARY token. What “failure” means
        is backend-defined (e.g., returning an Exception, raising, etc).

    OR
        An alternative that is considered as “one of several acceptable
        options” (e.g. first success wins), again backend-defined.
    """

    PRIMARY = auto()
    FALLBACK = auto()
    OR = auto()


@dataclass(frozen=True, slots=True)
class StepToken:
    """
    Atomic structural token used by the DSL.

    Attributes
    ----------
    value:
        Opaque payload. The DSL does not interpret this. Common choices:

            - a callable step
            - a backend-specific configuration object
            - a symbolic rule identifier
            - any other object meaningful to the backend

    relation:
        Structural relation of this token within its cluster
        (PRIMARY, FALLBACK, OR).

    semantic:
        Optional opaque metadata attached to this token only.
        Backends are free to interpret this as “semantic policy”,
        “label”, “Principle”, etc.
    """

    value: Step
    relation: Relation = Relation.PRIMARY
    semantic: Any | None = None


# A cluster is a tuple of StepToken objects.
#
# The DSL enforces *no* additional invariants at this level beyond
# structural ordering. Backends may choose to interpret the first
# token as PRIMARY and the rest as FALLBACK/OR according to each
# token's `relation`.
Cluster = Tuple[StepToken, ...]


# A sequence of clusters belonging to a single phase/section.
Clusters = Tuple[Cluster, ...]


@dataclass(frozen=True, slots=True)
class Section:
    """
    Phase-specific chain of clusters with an optional semantic token.

    Example (DSL):

        SET >> f1 << fb1 | fb2 >> f2 | f2b @ semantic_token

    Becomes structurally:

        Section(
            phase=SET.key,
            clusters=(
                (
                    StepToken(value=f1,  relation=Relation.PRIMARY),
                    StepToken(value=fb1, relation=Relation.FALLBACK),
                    StepToken(value=fb2, relation=Relation.FALLBACK),
                ),
                (
                    StepToken(value=f2,  relation=Relation.PRIMARY),
                    StepToken(value=f2b, relation=Relation.OR),
                ),
            ),
            semantic=semantic_token,
        )

    The DSL does not interpret `semantic`. Backends are free to.
    """

    phase: DSLPhaseKey
    clusters: Clusters
    semantic: Any | None = None
