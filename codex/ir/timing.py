# =============================================================================
# architech/codex/ir/timing.py
# =============================================================================
"""
Timing — WHEN an Output should be applied.

There are exactly two meaningful timing points in Codex:

CLUSTER
    Apply immediately when a pipeline (cluster chain) produces a result.

PHASE
    Defer application until the entire Codex execution completes
    (descriptor-call boundary).

There is intentionally no finer-grained timing.
"""

from __future__ import annotations
from enum import Enum, auto


class Timing(Enum):
    CLUSTER = auto()
    PHASE = auto()
