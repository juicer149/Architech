# ================================================================
# architech/codex/models.py
# ================================================================
"""
Codex IR Models (Intermediate Representation).

Responsibility
--------------
Convert high-level DSL structures (Section) into a compact,
backend-independent execution model consumed by CodexEngine.

Files using these models:
    • engine.py — for strict-first + semantic replay execution
    • codex.py  — for descriptor integration
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Tuple, Dict, Optional, Any

from dsl import Section, Cluster, StepToken, Relation
from .semantics import Principle, normalize_principle

StepFn = Callable[[Any], Any]


# ---------------------------------------------------------------
# Phase enum
# ---------------------------------------------------------------

class Phase(Enum):
    SET = auto()
    GET = auto()


# ---------------------------------------------------------------
# IR nodes
# ---------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ClusterSpec:
    """
    IR representation of a cluster of steps.

    A cluster may represent:

        - primary-only:
            primary, no fallbacks, no ors

        - primary+fallbacks:
            primary, fallbacks, no ors

        - primary+alternatives (OR):
            primary, no fallbacks, ors

    DSL invariants guarantee that a cluster will never mix
    FALLBACK and OR relations at the same time.
    """

    primary: StepFn
    fallbacks: Tuple[StepFn, ...]
    ors: Tuple[StepFn, ...]
    primary_name: str
    fallback_names: Tuple[str, ...]
    or_names: Tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SectionSpec:
    phase: Phase
    clusters: Tuple[ClusterSpec, ...]
    principle: Optional[Principle]


@dataclass(frozen=True, slots=True)
class PhaseSpec:
    phase: Phase
    sections: Tuple[SectionSpec, ...]


@dataclass(frozen=True, slots=True)
class CodexSpec:
    phases: Dict[Phase, PhaseSpec]
    # Precomputed flag: True iff any Section has a Principle.
    # This enables O(1) strict-mode auto detection in the engine.
    has_principles: bool


@dataclass(frozen=True, slots=True)
class CodexConfig:
    strict: Optional[bool]
    # Optional logger for semantic prints; defaults to `print` when None.
    # Signature should accept a single message string.
    logger: Optional[Callable[[str], None]] = None


# ---------------------------------------------------------------
# DSL → IR conversion
# ---------------------------------------------------------------
# borde dessa bo i en egen fil, kanske en builder.py och en converter.py?
def _phase_from_key(key: Any) -> Phase:
    """
    Map DSLPhaseKey to Codex Phase enum.

    Supported forms:
        - Phase.SET / Phase.GET (already correct)
        - string names "SET" / "GET"
    """
    if isinstance(key, Phase):
        return key
    if isinstance(key, str):
        try:
            return Phase[key]
        except KeyError:
            raise ValueError(f"Unsupported phase key string: {key!r}")
    raise TypeError(f"Unsupported phase key type: {type(key)!r} ({key!r})")


def _name_for_step(fn: StepFn) -> str:
    """Best-effort function name for debugging and error messages."""
    return getattr(fn, "__name__", repr(fn))


def section_from_dsl(node: Section) -> SectionSpec:
    """
    Convert a DSL Section into a SectionSpec.

    Interprets each cluster (tuple of StepToken) into:

        primary:   first token (must be Relation.PRIMARY)
        fallbacks: tokens with Relation.FALLBACK
        ors:       tokens with Relation.OR

    DSL invariants should ensure that a single cluster never mixes
    FALLBACK and OR relations at once.
    """
    phase = _phase_from_key(node.phase)
    principle = normalize_principle(node.semantic)

    clusters: list[ClusterSpec] = []

    for idx, cluster in enumerate(node.clusters):
        if not cluster:
            raise ValueError(f"Empty cluster at index {idx} in Section {node!r}")

        # First token is always PRIMARY
        first: StepToken = cluster[0]
        if first.relation is not Relation.PRIMARY:
            raise ValueError(
                f"First token in cluster {idx} must be PRIMARY, "
                f"got {first.relation!r}"
            )

        primary_fn = first.value  # type: ignore[assignment]

        rest = cluster[1:]
        fallbacks: Tuple[StepFn, ...] = ()
        ors: Tuple[StepFn, ...] = ()

        if rest:
            mode = rest[0].relation
            if mode is Relation.FALLBACK:
                # All must be FALLBACK
                for t in rest:
                    if t.relation is not Relation.FALLBACK:
                        raise ValueError(
                            "Cluster mixes FALLBACK with other relations; "
                            "this is not allowed."
                        )
                fallbacks = tuple(t.value for t in rest)  # type: ignore[assignment]
            elif mode is Relation.OR:
                # All must be OR
                for t in rest:
                    if t.relation is not Relation.OR:
                        raise ValueError(
                            "Cluster mixes OR with other relations; "
                            "this is not allowed."
                        )
                ors = tuple(t.value for t in rest)  # type: ignore[assignment]
            else:
                raise ValueError(
                    f"Unexpected relation {mode!r} in cluster {idx}; "
                    "expected FALLBACK or OR."
                )

        cluster_spec = ClusterSpec(
            primary=primary_fn,
            fallbacks=fallbacks,
            ors=ors,
            primary_name=_name_for_step(primary_fn),
            fallback_names=tuple(_name_for_step(f) for f in fallbacks),
            or_names=tuple(_name_for_step(f) for f in ors),
        )
        clusters.append(cluster_spec)

    return SectionSpec(
        phase=phase,
        clusters=tuple(clusters),
        principle=principle,
    )


def build_codex_spec(nodes: Tuple[Section, ...]) -> CodexSpec:
    """
    Build a CodexSpec from a tuple of DSL Sections.

    Sections are grouped by Phase, preserving insertion order.
    """
    per_phase: Dict[Phase, list[SectionSpec]] = {}

    for n in nodes:
        s = section_from_dsl(n)
        per_phase.setdefault(s.phase, []).append(s)

    phases: Dict[Phase, PhaseSpec] = {
        p: PhaseSpec(p, tuple(secs))
        for p, secs in per_phase.items()
    }
    # Precompute principle presence once for performance.
    has_principles = any(
        any(sec.principle is not None for sec in ps.sections)
        for ps in phases.values()
    )
    return CodexSpec(phases, has_principles)
