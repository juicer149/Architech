# =============================================================================
# architech/codex/ir/phase.py
# =============================================================================
"""
(1) Phase — IntFlag phases for Codex execution.

A Phase is a high-level lifecycle event. The runtime routes descriptor calls
(__get__/__set__/__delete__) to Phase.GET/SET/DELETE.

Phases are IntFlags to allow future combinations if needed.
"""

from __future__ import annotations

from enum import IntFlag, auto


class Phase(IntFlag):
    SET = auto()
    GET = auto()
    DELETE = auto()
