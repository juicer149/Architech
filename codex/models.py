# ================================================================
# Architech/codex/models.py
# ================================================================
"""
Codex IR Models (Intermediate Representation)

Responsibility
--------------
Convert high-level DSL (StepChain/SectionNode) into a compact,
backend-independent execution model consumed by CodexEngine.

Files using these models:
    • engine.py — for strict-first + semantic replay execution
    • codex.py  — for descriptor integration

Key IR structures:
    PhaseSpec  → holds ordered sections for SET/GET
    SectionSpec→ semantic policy + clusters
    ClusterSpec→ primary + fallback callables with metadata
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple, Dict, Optional

from dsl import SectionNode
from dsl import StepFn
from .semantics import Principle, normalize_principle


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
    primary: StepFn
    primary_name: str
    fallbacks: Tuple[StepFn, ...]
    fallback_names: Tuple[str, ...]


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


@dataclass(frozen=True, slots=True)
class CodexConfig:
    strict: Optional[bool]


# ---------------------------------------------------------------
# DSL → IR conversion
# ---------------------------------------------------------------
def _phase_from_key(key) -> Phase:
    if isinstance(key, Phase):
        return key
    try:
        return Phase[key]
    except Exception:
        raise ValueError(f"Unsupported phase key: {key!r}")


def section_from_dsl(node: SectionNode) -> SectionSpec:
    phase = _phase_from_key(node.phase)
    principle = normalize_principle(node.semantic)

    clusters = []
    for c in node.clusters:
        primary = c.primary.fn
        fallbacks = tuple(f.fn for f in c.fallbacks)

        clusters.append(
            ClusterSpec(
                primary=primary,
                primary_name=primary.__name__,
                fallbacks=fallbacks,
                fallback_names=tuple(f.__name__ for f in fallbacks),
            )
        )

    return SectionSpec(
        phase=phase,
        clusters=tuple(clusters),
        principle=principle,
    )


def build_codex_spec(nodes: Tuple[SectionNode, ...]) -> CodexSpec:
    per_phase: Dict[Phase, list[SectionSpec]] = {}

    for n in nodes:
        s = section_from_dsl(n)
        per_phase.setdefault(s.phase, []).append(s)

    # stable insertion order
    phases = {
        p: PhaseSpec(p, tuple(secs))
        for p, secs in per_phase.items()
    }
    return CodexSpec(phases)
