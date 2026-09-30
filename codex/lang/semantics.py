# =============================================================================
# codex/lang/semantics.py
# =============================================================================
"""
Semantic vocabulary for Codex.

This module defines the **semantic language** used to annotate pipelines.

Key concepts
------------
- Principle: *what kind* of semantic event this is (error, warning, info)
- Praxis: *how and when* violations are handled

Semantics are *descriptive*, not imperative.
Actual behavior is applied later by runtime routing.
"""

from __future__ import annotations

from ..ir.semantics import Praxis, Principle

# ---------------------------------------------------------------------------
# Praxis presets
# ---------------------------------------------------------------------------
# add on when you apply actions as of when something should happen
# like for example action = CLUSTER, PHASE, CODEX = True, False, None
#: Abort execution immediately (fail-fast)
PRAXIS_ABORT = Praxis(action="raise")

#: Print warning but continue
PRAXIS_WARN = Praxis(action="print")

#: Informational (no control-flow impact)
PRAXIS_INFO = Praxis(action="ignore")

#: Completely silent
PRAXIS_IGNORE = Praxis(action="ignore")

# ---------------------------------------------------------------------------
# Principle presets
# ---------------------------------------------------------------------------

ERROR = Principle("error", PRAXIS_ABORT)
WARNING = Principle("warning", PRAXIS_WARN)
INFO = Principle("info", PRAXIS_INFO)
IGNORE = Principle("ignore", PRAXIS_IGNORE)

__all__ = [
    "Praxis",
    "Principle",
    "PRAXIS_ABORT",
    "PRAXIS_WARN",
    "PRAXIS_INFO",
    "PRAXIS_IGNORE",
    "ERROR",
    "WARNING",
    "INFO",
    "IGNORE",
]
