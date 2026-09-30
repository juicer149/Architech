# =============================================================================
# codex/lang/output.py
# =============================================================================
"""
Output routing primitives for Codex.

This module defines **preconfigured Output objects** that describe
*how results are routed* after pipeline execution.

These are *language-level building blocks* — not policies.

Design principles
-----------------
- Outputs are pure data
- No side effects
- No domain assumptions
- Safe defaults
"""

from __future__ import annotations

from typing import Any

from ..ir.output import Output, SELF, RETURN, DROP

# ---------------------------------------------------------------------------
# Value outputs (non-exception)
# ---------------------------------------------------------------------------

#: Write result back to instance storage (descriptor default for SET)
WRITE_SELF = Output(
    is_exception=False,
    enabled=True,
    dest=SELF,
)

#: Return result from descriptor (__get__)
WRITE_RETURN = Output(
    is_exception=False,
    enabled=True,
    dest=RETURN,
)

#: Drop result entirely
WRITE_DROP = Output(
    is_exception=False,
    enabled=True,
    dest=DROP,
)

# ---------------------------------------------------------------------------
# Exception outputs
# ---------------------------------------------------------------------------

#: Raise exception (default exception behavior)
EXC_RAISE = Output(
    is_exception=True,
    enabled=True,
    dest=RETURN,
)

#: Drop exception (silently ignore)
EXC_DROP = Output(
    is_exception=True,
    enabled=True,
    dest=DROP,
)

__all__ = [
    "WRITE_SELF",
    "WRITE_RETURN",
    "WRITE_DROP",
    "EXC_RAISE",
    "EXC_DROP",
]
