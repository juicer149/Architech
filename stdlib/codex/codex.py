# ================================================================
# Architech/stdlib/codex/codex.py
# ================================================================
"""
High-level Codex building blocks (stdlib).

Defines reusable Codex pipelines built from:
    - stdlib phase tokens (SET / GET)
    - stdlib principles (ERROR, ...)
    - stdlib validators/transformers

Example:

    from stdlib.codex.codex import IS_INT, POSITIVE, CLEAN_EMAIL

    class User:
        age = IS_INT + POSITIVE
        email = CLEAN_EMAIL
"""

from __future__ import annotations

from .stdcodex import StdCodex
from .phases import SET
from .principles import ERROR
from .validators.numbers import is_int, positive, in_range
from .validators.email import require_at
from .transformers.email import normalize_email


# ---------------------------------------------------------------
# Numeric Codex building blocks
# ---------------------------------------------------------------

# "value must be interpretable as int"
IS_INT = StdCodex(SET >> is_int | ERROR)

# "value must be >= 0" (assumes numeric)
POSITIVE = StdCodex(SET >> positive | ERROR)


def IN_RANGE(min_val=None, max_val=None) -> StdCodex:
    """
    Build a Codex requiring that the value lies within [min_val, max_val].

    Example:
        AGE_RANGE = IN_RANGE(0, 150)

        class User:
            age = IS_INT + AGE_RANGE
    """
    return StdCodex(SET >> in_range(min_val, max_val) | ERROR)


# ---------------------------------------------------------------
# Email Codex building blocks
# ---------------------------------------------------------------

CLEAN_EMAIL = StdCodex(SET >> normalize_email >> require_at | ERROR)
