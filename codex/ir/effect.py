# =============================================================================
# architech/codex/ir/effect.py
# =============================================================================
"""
Effect — WHAT kind of side-effect an Output represents.

This module defines *what* happens when a value or exception leaves
the execution pipeline.

Design principles
-----------------
- Effect is purely declarative (data, not behavior).
- Effect never performs actions itself.
- Runtime decides *how* to realize each Effect.

Effects
-------
INHERENT
    Built-in Codex behavior.
    - values: written to SELF (SET) or returned (GET)
    - exceptions: raised

CUSTOM
    Delegate effect execution to a user-provided hook.

DROP
    Explicitly do nothing.
    No write, no return, no raise.
"""
from __future__ import annotations

from enum import Enum, auto


class Effect(Enum):
    INHERENT = auto()
    CUSTOM = auto()
    DROP = auto()
