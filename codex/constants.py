# ================================================================
# architech/codex/constants.py
# ================================================================
"""
Default semantic presets for Codex.

Responsibility
--------------
Defines reusable Praxis/Principle presets such as ERROR, WARN, INFO,
and IGNORE.

Why separate from semantics.py?
--------------------------------
    • semantics.py defines *what* Praxis and Principle ARE.
    • constants.py defines *how they are commonly used*.
"""

from __future__ import annotations

from .semantics import Praxis, Principle

# Default praxis used when user provides only a string semantic token.
#
# Timing=True  → treated as cluster-level by default.
# Action=None  → ignore, unless backends decide otherwise.
DEFAULT_PRAXIS = Praxis(
    timing=True,
    action=None,
)

# allt härifrån och nedåt tillhör stdlib/codex/ antingen praxis.py eller principle.py
# enda man kunde addera hade varit att haft något för timing och action
# kanske
# Common praxis presets
ABORT = Praxis(True, True)
FATAL_P = Praxis(True, True)
WARN_P = Praxis(False, False)
INFO_P = Praxis(False, False)
IGNORE_P = Praxis(None, None)


class FatalError(RuntimeError):
    """Raised for fatal semantic violations."""
    pass


# High-level Principle presets
ERROR = Principle("error", ABORT, RuntimeError)
FATAL = Principle("fatal", FATAL_P, FatalError)
WARN = Principle("warn", WARN_P)
INFO = Principle("info", INFO_P)
IGNORE = Principle("ignore", IGNORE_P)
