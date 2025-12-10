# ================================================================
# stdlib/codex/principles.py
# ================================================================
"""
Standard semantic Principles for Codex stdlib.

We distinguish between:

    - Praxis names (ABORT, WARN, INFO, SILENT)
      → *how/when* we act

    - Principle names (ERROR, FATAL, WARN_P, INFO_P, IGNORE_P)
      → *what kind* of semantic level (error/warn/info/ignore)

This module is mostly a thin aliasing layer around codex.constants.
"""

from __future__ import annotations
# alla dessa hade kunnat bo här istället för i codex.constants
from codex.constants import (
    ERROR as ERROR,
    FATAL as FATAL,
    WARN as WARN,
    INFO as INFO,
    IGNORE as IGNORE,
    ABORT as ABORT,
    FATAL_P as FATAL_P,
    WARN_P as WARN_P,
    INFO_P as INFO_P,
    IGNORE_P as IGNORE_P,
    FatalError as FatalError,
)

__all__ = [
    "ERROR",
    "FATAL",
    "WARN",
    "INFO",
    "IGNORE",
    "ABORT",
    "FATAL_P",
    "WARN_P",
    "INFO_P",
    "IGNORE_P",
    "FatalError",
]
