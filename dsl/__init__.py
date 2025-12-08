# ================================================================
# architech/dsl/__init__.py
# ================================================================
"""
Pure DSL front-end for Architech pipelines (e.g., Codex).

This package defines a syntax-building layer that is entirely decoupled
from runtime semantics or backend execution engines.

Conceptually, the DSL does three things:

    1. Provides a generic notion of a *phase token*:
           PhaseTokenBase(phase_key)

       Backends construct concrete tokens (SET, GET, etc.) by
       instantiating PhaseTokenBase with domain-specific phase keys.

    2. Defines structural nodes for pipelines:
           StepNode, ClusterNode, SectionNode

       These are purely structural AST-like nodes. They do not know
       about semantics, Principles, Praxis, or execution behaviour.

    3. Exposes a small fluent DSL:

           SET >> f1 << fb1 << fb2 >> f2 | semantic_token

       which becomes an immutable SectionNode backend implementations
       can interpret into their own IR.

Backends interpret:

    - `phase`       via their own Phase/enum system
    - `clusters`    as primary+fallback step blocks
    - `semantic`    as an opaque annotation

This keeps the DSL layer simple, reusable, and backend-agnostic.
"""

from .protocol import DSLPhaseKey, StepFn
from .phase_token import PhaseTokenBase
from .nodes import StepNode, ClusterNode, SectionNode
from .syntax import StepChain

__all__ = [
    "DSLPhaseKey",
    "StepFn",
    "PhaseTokenBase",
    "StepChain",
    "StepNode",
    "ClusterNode",
    "SectionNode",
]
