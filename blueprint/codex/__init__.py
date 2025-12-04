# ================================================================
# blueprint/codex/__init__.py
# ================================================================
"""
Codex — declarative semantic pipelines over the generic DSL.

This package wires together:

    - blueprint.dsl:
        StepChain, PhaseTokenBase (pure syntax, no semantics)
    - Codex runtime:
        Phase enum (SET/GET), IR models, bindings, pipeline compiler
    - control layer:
        Principle, Panopticon, etc. (via semantics + pipeline)

Public surface
--------------

High-level usage:

    from blueprint.codex import Codex, SET, GET, ERROR, WARN

    class Email:
        address = Codex[
            SET(strict=True) >> normalize >> validate | ERROR,
            GET >> mask_for_display | WARN,
        ]

The user-facing DSL objects are:

    - SET, GET      → phase tokens (assignment / access)
    - StepChain     → returned by SET/GET >> fn

Codex then consumes StepChain + bare callables and builds an executable
two-phase pipeline (SET/GET) that can run in strict or interpreted mode.
"""

from __future__ import annotations

from ..dsl import StepChain, PhaseTokenBase

from .codex import Codex
from .models import (
    Fn,
    Step,
    Section,
    Phase,
    CodexConfig,
    PhaseConfig,
)
from control.semantics import (
    ERROR,
    FATAL,
    WARN,
    IGNORE,
    CRITICAL,
    INFO,
    to_principle,
)

# Phase-level DSL tokens specific to Codex:
#   SET  → runs on attribute assignment (Phase.SET)
#   GET  → runs on attribute access (Phase.GET)
SET = PhaseTokenBase(phase_key=Phase.SET, phase_kwargs={})
GET = PhaseTokenBase(phase_key=Phase.GET, phase_kwargs={})

__all__ = [
    # Descriptor
    "Codex",
    # DSL bridge
    "SET",
    "GET",
    "StepChain",
    # IR models
    "Fn",
    "Step",
    "Section",
    "Phase",
    "CodexConfig",
    "PhaseConfig",
    # Semantics
    "ERROR",
    "FATAL",
    "WARN",
    "IGNORE",
    "CRITICAL",
    "INFO",
    "to_principle",
]
