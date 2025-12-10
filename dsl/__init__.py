# ================================================================
# architech/dsl/__init__.py
# ================================================================
"""
Architech DSL — a pure structural front-end for pipelines.

This package defines a *semantics-free* syntax layer that backends
(such as `codex`) can interpret into their own IR and execution
engines.

Conceptually, the DSL does three things:

    1. Provides a generic notion of a *phase token*:

           PhaseToken(phase_key)

       Backends construct concrete tokens (SET, GET, ...) by
       instantiating PhaseToken with domain-specific phase keys.

    2. Defines structural node types:

           Relation           — PRIMARY / FALLBACK / OR
           StepToken(value, relation, semantic)
           Section(phase, clusters, semantic)

       where:

           - clusters: tuple of clusters
           - a cluster: tuple of StepToken objects

       The DSL does *not* interpret these values; only the backend does.

    3. Exposes a small fluent DSL:

           SET >> f1 << fb1 | fb2 >> f2 | f2b @ semantic_token

       which becomes an immutable Section that backends can map into
       their own IR.

Backends interpret:

    - phase      according to their own Phase/enum system
    - clusters   as sequences of structurally related steps
    - relation   to distinguish PRIMARY/FALLBACK/OR tokens
    - semantic   as an opaque annotation (principle, label, policy, ...)

The DSL itself is completely backend-agnostic.
"""

from __future__ import annotations

from .protocol import DSLPhaseKey, Step
from .nodes import Relation, StepToken, Section, Cluster, Clusters
from .phases import PhaseToken
from .builder import StepChain

__all__ = [
    # protocols / base types
    "DSLPhaseKey",
    "Step",
    # structural nodes
    "Relation",
    "StepToken",
    "Cluster",
    "Clusters",
    "Section",
    # syntax / entrypoints
    "PhaseToken",
    "StepChain",
]
