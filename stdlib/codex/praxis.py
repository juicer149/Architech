# ================================================================
# Architech/stdlib/codex/praxis.py
# ================================================================
"""
Semantic timing + action vocabulary for Codex stdlib.

This module defines:
    - symbolic constants for Praxis.timing / Praxis.action
    - common Praxis presets (ABORT, WARN, INFO, SILENT)

The `Praxis` type itself comes from `codex.semantics`.
"""

from __future__ import annotations

from codex.semantics import Praxis

# ---------------------------------------------------------------
# Timing constants (Praxis.timing)
# ---------------------------------------------------------------
# Pure syntactic sugar — the engine only sees True/False/None.

CLUSTER: bool | None = True    # flush immediately (per cluster)
PHASE: bool | None = False     # flush at end of phase
CODEX: bool | None = None      # flush after entire Codex run


# ---------------------------------------------------------------
# Action constants (Praxis.action)
# ---------------------------------------------------------------
RAISE: bool | None = True      # raise exception
PRINT: bool | None = False     # print violation
IGNORE: bool | None = None     # ignore silently


# ---------------------------------------------------------------
# High-level Praxis presets
# ---------------------------------------------------------------
ABORT: Praxis = Praxis(CLUSTER, RAISE)    # fail-fast
WARN: Praxis = Praxis(PHASE, PRINT)       # warn but continue
INFO: Praxis = Praxis(PHASE, PRINT)       # informational messages
SILENT: Praxis = Praxis(CODEX, IGNORE)    # completely silent
