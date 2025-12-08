# ================================================================
# Architech/codex/__init__.py
# ================================================================
"""
Codex — Deterministic Semantic Pipelines for Python.

PHILOSOPHY
----------

Codex builds on four principles:

1. STRUCTURE BEFORE SEMANTICS  
   The DSL expresses only structure. Codex adds meaning via Praxis +
   Principle.

2. MINIMAL BOOLEAN SEMANTICS  
   A Principle is just:
       Praxis(timing=True/False/None, action=True/False/None)

   which controls WHEN and HOW semantic violations are handled.

3. STRICT-FIRST EXECUTION  
   First run everything in pure Python.
   If something fails and semantics are enabled, replay sections with
   semantic handling.

4. ZERO OVERHEAD DESIGN  
   No Panopticon, no capture layer, no global effect engines.
"""

from .semantics import Praxis, Principle
from .constants import (
    DEFAULT_PRAXIS,
    ERROR,
    FATAL,
    WARN,
    INFO,
    IGNORE,
)

from .codex import Codex
from .models import Phase

__all__ = [
    "Codex",
    "Phase",
    "Praxis",
    "Principle",
    "DEFAULT_PRAXIS",
    "ERROR",
    "FATAL",
    "WARN",
    "INFO",
    "IGNORE",
]
