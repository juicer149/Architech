# =============================================================================
# architech/codex/ir/pipeline.py
# =============================================================================
"""
(5) Pipeline — flat list of Nodes.

A Pipeline is an ordered list of Nodes. The Engine runs them sequentially.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .node import Node


@dataclass(slots=True)
class Pipeline:
    nodes: List[Node]
