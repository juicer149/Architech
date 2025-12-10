# ================================================================
# architech/codex/__init__.py
# ================================================================
"""
Codex — Deterministic Semantic Pipelines for Python.

High-level responsibilities
---------------------------
    • Provide a descriptor (`Codex`) for attaching pipelines to attributes.
    • Interpret structural DSL objects (`Section`, `StepChain`) into Codex IR.
    • Execute pipelines via a strict-first engine with optional semantics.

This package intentionally separates:

    - DSL (structure)       → architech.dsl
    - IR models             → codex.models
    - Semantics vocabulary  → codex.semantics / codex.constants
    - Execution engine      → codex.engine

Codex also defines the canonical SET/GET phase tokens for use with the DSL:

    from codex import SET, GET, Codex

    class User:
        name = Codex(
            SET >> normalize >> validate @ ERROR,
            GET >> normalize,
        )
"""

from __future__ import annotations

from dsl import PhaseToken

from .semantics import Praxis, Principle, normalize_principle
from .constants import (
    DEFAULT_PRAXIS,
    ERROR,
    FATAL,
    WARN,
    INFO,
    IGNORE,
    ABORT,
    FATAL_P,
    WARN_P,
    INFO_P,
    IGNORE_P,
)
from .models import Phase
from .codex import Codex

# ------------------------------------------------------------------
# Canonical phase tokens for Codex
# ------------------------------------------------------------------

#: Phase token for write/update operations.
SET = PhaseToken(Phase.SET)

#: Phase token for read/access operations.
GET = PhaseToken(Phase.GET)


__all__ = [
    # Core descriptor / phases
    "Codex",
    "Phase",
    "SET",
    "GET",
    # Semantics
    "Praxis",
    "Principle",
    "normalize_principle",
    # Principles / praxis presets
    "DEFAULT_PRAXIS",
    "ERROR",
    "FATAL",
    "WARN",
    "INFO",
    "IGNORE",
    "ABORT",
    "FATAL_P",
    "WARN_P",
    "INFO_P",
    "IGNORE_P",
]
