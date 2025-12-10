# ================================================================
# stdlib/codex/praxis.py
# ================================================================
"""
Semantic timing + action vocabulary for Codex stdlib.

This module defines:

    - symbolic constants for Praxis.timing / Praxis.action
    - a few common Praxis presets (ABORT, WARN, INFO, SILENT)

The type `Praxis` comes from the core module `codex.semantics`.

NOTE:
    Codex already ships with presets in `codex.constants`
    (ABORT, FATAL_P, WARN_P, INFO_P, IGNORE_P). This stdlib
    module provides extra symbolic sugar and aliases.
"""

from __future__ import annotations

from codex.semantics import Praxis
from codex.constants import (
    ABORT as CORE_ABORT,
    WARN_P as CORE_WARN_P,
    INFO_P as CORE_INFO_P,
    IGNORE_P as CORE_IGNORE_P,
)

# funderar på om timing och actions borde bo i cosntants.py i codex/ istället
# då kan även koden se renare ut via istället frö att det står att den kontrollerar
# mot bool kan den bara skriva if praxis.timing is CLUSTER and praxis.action is RAISE
# osv?
# ---------------------------------------------------------------
# Timing constants (Praxis.timing)
# ---------------------------------------------------------------
# These are purely syntactic sugar — the engine only sees True/False/None.

CLUSTER: bool | None = True    # flush immediately (per cluster)
PHASE: bool | None = False     # flush at end of phase
CODEX: bool | None = None      # flush after the entire Codex run

# ---------------------------------------------------------------
# Action constants (Praxis.action)
# ---------------------------------------------------------------
RAISE: bool | None = True      # raise exception
PRINT: bool | None = False     # print violation
IGNORE: bool | None = None     # ignore silently

# ---------------------------------------------------------------
# High-level Praxis presets
# ---------------------------------------------------------------
# We alias Codex's presets for consistency, but also expose
# short, descriptive names here.

ABORT: Praxis = CORE_ABORT          # fail-fast
WARN: Praxis = CORE_WARN_P          # warn but continue
INFO: Praxis = CORE_INFO_P          # informational messages
SILENT: Praxis = CORE_IGNORE_P      # completely silent
