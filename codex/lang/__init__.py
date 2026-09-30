# =============================================================================
# codex/lang/__init__.py
# =============================================================================
"""
Codex language primitives.

This package defines the **core vocabulary** of Codex:

- phases
- routing primitives
- semantic labels

It intentionally does *not* define domain logic or policies.
"""

from .phase import SET, GET, DELETE
from .output import (
    WRITE_SELF,
    WRITE_RETURN,
    WRITE_DROP,
    EXC_RAISE,
    EXC_DROP,
)
from .semantics import (
    Praxis,
    Principle,
    ERROR,
    WARNING,
    INFO,
    IGNORE,
)

__all__ = [
    # phases
    "SET",
    "GET",
    "DELETE",
    # outputs
    "WRITE_SELF",
    "WRITE_RETURN",
    "WRITE_DROP",
    "EXC_RAISE",
    "EXC_DROP",
    # semantics
    "Praxis",
    "Principle",
    "ERROR",
    "WARNING",
    "INFO",
    "IGNORE",
]
