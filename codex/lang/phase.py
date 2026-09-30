# =============================================================================
# codex/lang/phase.py
# =============================================================================
"""
Phase tokens for the Codex DSL.

This module exposes **canonical phase tokens** used to build DSL expressions:

    SET >> step >> step
    GET >> step
    DELETE >> step

These tokens are thin wrappers around the Codex Phase enum via DSL PhaseToken.

Design notes
------------
- Phase tokens belong to the *language*, not stdlib
- They define *when* a pipeline runs, not *what* it does
- No defaults, no policies, no behavior here
"""

from __future__ import annotations

from dsl import PhaseToken
from ..ir.phase import Phase

# ---------------------------------------------------------------------------
# Canonical phase tokens
# ---------------------------------------------------------------------------

#: Assignment / mutation phase
SET = PhaseToken(Phase.SET)

#: Access / read phase
GET = PhaseToken(Phase.GET)

#: Deletion phase
DELETE = PhaseToken(Phase.DELETE)

__all__ = ["SET", "GET", "DELETE"]
