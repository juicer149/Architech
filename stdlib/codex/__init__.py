# ================================================================
# Architech/stdlib/codex/__init__.py
# ================================================================
"""
Stdlib for Codex — reusable semantic building blocks.

This package lives *above* the core module `architech/codex/` and
exposes three things:

1. Semantic vocabulary
   - Time/action constants (CLUSTER, PHASE, CODEX, RAISE, PRINT, IGNORE)
   - Praxis presets: ABORT, WARN, INFO, SILENT
   - Principles: ERROR, FATAL, WARN_P, INFO_P, IGNORE_P

2. Phase tokens
   - SET  → pipelines executed on assignment (Phase.SET)
   - GET  → pipelines executed on attribute read (Phase.GET)

3. StdCodex + ready-made pipelines
   - StdCodex: thin wrapper around `codex.Codex` for stdlib usage
   - (Optional) prebuilt Codex building blocks in `stdlib/codex/codex.py`

The goals are:
    - keep core-Codex minimal and semantics-agnostic
    - let stdlib/codex provide “batteries included” semantics
    - allow usage like:

        from stdlib.codex import SET, GET, ERROR
        from stdlib.codex.stdlib_codex import StdCodex

        class User:
            age = StdCodex(SET >> to_int | ERROR)

without needing to care about engine/IR details.
"""

from .praxis import (
    CLUSTER,
    PHASE,
    CODEX,
    RAISE,
    PRINT,
    IGNORE,
    ABORT,
    WARN,
    INFO,
    SILENT,
)

from .principles import (
    ERROR,
    FATAL,
    WARN_P,
    INFO_P,
    IGNORE_P,
)

from .phases import SET, GET
from .stdcodex import StdCodex

__all__ = [
    # Praxis constants
    "CLUSTER",
    "PHASE",
    "CODEX",
    "RAISE",
    "PRINT",
    "IGNORE",
    "ABORT",
    "WARN",
    "INFO",
    "SILENT",
    # Principles
    "ERROR",
    "FATAL",
    "WARN_P",
    "INFO_P",
    "IGNORE_P",
    # Phase tokens
    "SET",
    "GET",
    # Stdlib Codex wrapper
    "StdCodex",
]
