# ================================================================
# Architech/stdlib/codex/principles.py
# ================================================================
"""
Standard semantic Principles for Codex stdlib.

Distinguish:
    - Praxis names (ABORT, WARN, INFO, SILENT) → *how/when* we act
    - Principle names (ERROR, FATAL, WARN_P, INFO_P, IGNORE_P)
      → *what semantic severity level* we attach (error/warn/info/ignore)
"""

from __future__ import annotations

from codex.semantics import Principle
from .praxis import ABORT, WARN, INFO, SILENT


class FatalError(RuntimeError):
    """Default fatal exception type for FATAL principles."""
    pass


# ---------------------------------------------------------------
# Principles
# ---------------------------------------------------------------
ERROR = Principle("error", ABORT, RuntimeError)
FATAL = Principle("fatal", ABORT, FatalError)

# Suffix _P avoids name clash with praxis.WARN/INFO.
WARN_P = Principle("warn", WARN)
INFO_P = Principle("info", INFO)
IGNORE_P = Principle("ignore", SILENT)
