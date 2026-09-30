# =============================================================================
# architech/codex/runtime/__init__.py
# =============================================================================
"""
Codex runtime layer.

This package contains the *imperative execution machinery* of Codex.

Architectural role
------------------
The runtime layer is responsible for **executing compiled IR** and
**materializing effects**.

It is the ONLY layer allowed to:
- mutate instances
- raise runtime exceptions
- emit warnings
- call user hooks

Responsibilities
----------------
- Execute pipelines (Engine)
- Bind execution to Python descriptor protocol (DescriptorRouting)
- Coordinate deferred effects (ExecutionContext)

Non-API
-------
This package is NOT part of the public API.
It may change freely as long as IR and top-level Codex behavior remain stable.
"""

from __future__ import annotations

from .engine import Engine
from .routing import DescriptorRouting
from .context import ExecutionContext

__all__ = [
    "Engine",
    "DescriptorRouting",
    "ExecutionContext",
]
