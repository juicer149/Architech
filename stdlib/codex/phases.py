# ================================================================
# stdlib/codex/phases.py
# ================================================================
"""
Canonical phase tokens for stdlib.

Responsibility
--------------
Expose ready-made `SET` and `GET` tokens based on Codex Phase enum.

These are thin wrappers around the DSL PhaseToken. They are used as
the entrypoints into the DSL:

    from stdlib.codex import SET, GET

    name_rules = StdCodex(
        (SET >> strip >> non_empty) @ WARN,
        (GET >> normalize) @ INFO,
    )
"""

from __future__ import annotations

from dsl import PhaseToken
from codex.models import Phase

# Stdlib phase tokens used everywhere
SET = PhaseToken(Phase.SET)
GET = PhaseToken(Phase.GET)

__all__ = ["SET", "GET"]
