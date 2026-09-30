# ================================================================
# stdlib/codex/__init__.py
# ================================================================
"""
Stdlib layer on top of Codex + DSL.

Responsibility
--------------
Provides:

    • Canonical phase tokens:
         SET, GET

    • Ready-to-use Codex descriptor:
         StdCodex

    • Common semantic presets (re-exported from codex.constants):
         ERROR, FATAL, WARN, INFO, IGNORE
         DEFAULT_PRAXIS
         ABORT, FATAL_P, WARN_P, INFO_P, IGNORE_P

    • Frequently used composite pipelines:
         IS_INT, POSITIVE, IN_RANGE, NON_EMPTY_STR,
         NORMALIZED_TEXT, CLEAN_EMAIL

    • Primitive validators / transformers under:
         stdlib.codex.validators.*
         stdlib.codex.transformers.*
"""

from __future__ import annotations

from .phases import SET, GET
from .stdlib_codex import StdCodex
from .codex import (
    IS_INT,
    POSITIVE,
    IN_RANGE,
    NON_EMPTY_STR,
    NORMALIZED_TEXT,
    CLEAN_EMAIL,
)

from codex.semantics import Praxis, Principle
from codex.constants import (
    DEFAULT_PRAXIS,
    ERROR,
    FATAL,
    WARN,
    INFO,
    IGNORE,
    ABORT,
    FATAL_P,
    WARN_P,
    INFO_P,
    IGNORE_P,
)

__all__ = [
    # phases
    "SET",
    "GET",
    # core Codex re-exports
    "StdCodex",
    "Praxis",
    "Principle",
    # principles
    "DEFAULT_PRAXIS",
    "ERROR",
    "FATAL",
    "WARN",
    "INFO",
    "IGNORE",
    # praxis presets
    "ABORT",
    "FATAL_P",
    "WARN_P",
    "INFO_P",
    "IGNORE_P",
    # composite stdlib codices
    "IS_INT",
    "POSITIVE",
    "IN_RANGE",
    "NON_EMPTY_STR",
    "NORMALIZED_TEXT",
    "CLEAN_EMAIL",
]
