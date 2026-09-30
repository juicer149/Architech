# =============================================================================
# architech/codex/ir/node.py
# =============================================================================
"""
(4) Node — compiled execution unit.

A Node is the compiled form of a single DSL cluster.

Structure
---------
- fn:
    Primary step function.
- fallbacks:
    Optional fallback steps (FALLBACK semantics).
- ors:
    Optional OR-alternative steps (OR semantics).

Notes
-----
- Node contains NO routing or semantic policy.
- Node does NOT know about Output, Effect, Timing, labels, or routing.
- Execution semantics are implemented in runtime/engine.py.

Node is pure structure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Tuple

StepFn = Callable[[Any], Any]


@dataclass(slots=True)
class Node:
    fn: StepFn
    fallbacks: Tuple[StepFn, ...] = ()
    ors: Tuple[StepFn, ...] = ()
