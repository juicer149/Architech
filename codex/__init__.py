# ================================================================
# architech/codex/__init__.py
# ================================================================
"""
Codex — execution and routing engine for Architech DSL.

This package provides stable, user-facing concepts only.

Exposed concepts
----------------
• Codex
    Descriptor / callable that binds DSL Sections to execution.

• Phase
    Canonical execution phases (SET / GET / DELETE).

• Principle / Praxis
    Semantic metadata attached via the DSL (@ operator).

• Output
    Declarative routing policy for values and exceptions.

• Effect / Timing
    Enumerations describing WHAT happens and WHEN it happens.

Internal layers (compiler/, runtime/, ir/) are intentionally hidden.
"""

from __future__ import annotations

# ----------------------------------------------------------------
# Core user-facing objects
# ----------------------------------------------------------------

from .codex import Codex
from .ir.phase import Phase

# ----------------------------------------------------------------
# Semantic primitives
# ----------------------------------------------------------------

from .ir.semantics import Principle, Praxis
from .ir.output import Output
from .ir.effect import Effect
from .ir.timing import Timing

# ----------------------------------------------------------------
# Language-level presets (user convenience)
# ----------------------------------------------------------------

from .lang import (
    ERROR,
    WARNING,
    WRITE,
    DROP,
)

# ----------------------------------------------------------------
# Public API
# ----------------------------------------------------------------

__all__ = [
    # core
    "Codex",
    "Phase",

    # semantics
    "Principle",
    "Praxis",

    # output
    "Output",
    "Effect",
    "Timing",

    # lang presets
    "ERROR",
    "WARNING",
    "WRITE",
    "DROP",
]
