# ================================================================
# Architech/codex/constants.py
# ================================================================
"""
Default semantic presets for Codex.

Responsibility
--------------
This module defines reusable Praxis/Principle presets such as ERROR,
WARN, INFO, and IGNORE.

Why separate from semantics.py?
--------------------------------
• semantics.py defines *what* Praxis and Principle ARE.
• constants.py defines *how they are commonly used*.

These values can be imported directly by users of Codex.
"""
from __future__ import annotations
from .semantics import Praxis, Principle

# allt som ska bo i denna efter refaktorisering är DEFAULT parameters för ex:
# DEFAULT_PRAXIS
# DEFAULT_PRINCIPLE
# DEFAULT_PHASE

# Default praxis used when user provides only a string-semantic
DEFAULT_PRAXIS = Praxis(
    timing=True,      # cluster-level
    action=None       # ignore
)

# Ska tas bort, dessa ska numera bo i architech/stdlib/codex/praxis.py
# Common praxis presets
ABORT = Praxis(True, True)
FATAL_P = Praxis(True, True)
WARN_P = Praxis(False, False)
INFO_P = Praxis(False, False)
IGNORE_P = Praxis(None, None)

#denna ska bort och läggas i architech/stdlib/codex/exceptions.py
class FatalError(RuntimeError):
    """Raised for fatal semantic violations."""
    pass

# denna ska med bort och läggas i architech/stdlib/codex/principles.py
# High-level presets
ERROR = Principle("error", ABORT, RuntimeError)
FATAL = Principle("fatal", FATAL_P, FatalError)
WARN = Principle("warn", WARN_P)
INFO = Principle("info", INFO_P)
IGNORE = Principle("ignore", IGNORE_P)
