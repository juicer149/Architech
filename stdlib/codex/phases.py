# ================================================================
# Architech/stdlib/codex/phases.py
# ================================================================
"""
Codex-specific phase tokens for the DSL: SET and GET.

These bind together:
    - DSL PhaseTokenBase
    - Codex Phase enum (Phase.SET / Phase.GET)

Example:
    from stdlib.codex import SET, GET, StdCodex, ERROR

    class User:
        age = StdCodex(SET >> to_int | ERROR)
"""

from __future__ import annotations

from dsl import PhaseTokenBase
from codex.models import Phase

# Phase-level DSL tokens specific to Codex:
#   SET → executed on attribute assignment (Phase.SET)
#   GET → executed on attribute read (Phase.GET)
SET: PhaseTokenBase = PhaseTokenBase(Phase.SET)
GET: PhaseTokenBase = PhaseTokenBase(Phase.GET)
