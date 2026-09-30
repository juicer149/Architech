# =============================================================================
# architech/codex/runtime/plan.py
# =============================================================================
"""
Runtime plans — frozen execution-ready structures.

Purpose
-------
This module defines the boundary between:
- IR (compiler output)
- runtime execution (Engine)

Design goals
------------
- immutable
- cache-friendly
- no mutation in hot paths
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from ..ir.node import Node


@dataclass(frozen=True, slots=True)
class RuntimePipeline:
    """
    Immutable, tuple-backed pipeline for execution.
    """
    nodes: Tuple[Node, ...]


@dataclass(frozen=True, slots=True)
class RuntimePhasePlan:
    """
    Runtime representation of a PhasePlan.
    """
    pipeline: RuntimePipeline
