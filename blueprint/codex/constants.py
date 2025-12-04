# ================================================================
# blueprint/codex/constants.py
# ================================================================
"""
Global default configuration values for Codex.

This module centralizes system-level defaults used by:

    - semantics.py (Principle synthesis)
    - the Codex descriptor (default phase, future knobs)

Rationale
---------
Keeping these values here:

    • avoids cyclic imports between codex modules,
    • keeps system defaults easy to inspect or override,
    • separates:
        - semantic defaults (labels/praxis/effect),
        - structural defaults (e.g. default Phase).
"""

from __future__ import annotations

from control.config import Praxis, Effect
from .models import Phase

# ---------------------------------------------------------------------------
# Semantic defaults used when synthesizing Principles
# ---------------------------------------------------------------------------

#: Default diagnostic label when user does not provide one.
DEFAULT_LABEL: str = "architech"

#: Default praxis to use when inferring a Principle from a string/bool.
#: Convention: immediate realization; typically combined with RAISE.
DEFAULT_PRAXIS: Praxis = Praxis.IMMEDIATE

#: Default effect for synthesized Principles.
#: Convention: treat semantic failures as exceptions.
DEFAULT_EFFECT: Effect = Effect.RAISE

# ---------------------------------------------------------------------------
# Structural defaults
# ---------------------------------------------------------------------------

#: Default phase used when a bare function is passed to Codex without
#: an explicit SET/GET DSL wrapper.
DEFAULT_PHASE: Phase = Phase.SET

__all__ = [
    "DEFAULT_LABEL",
    "DEFAULT_PRAXIS",
    "DEFAULT_EFFECT",
    "DEFAULT_PHASE",
]
