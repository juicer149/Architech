# ================================================================
# stdlib/codex/codex.py
# ================================================================
"""
High-level Codex building blocks (stdlib).

Here we define reusable Codex pipelines built on:

    - stdlib phase tokens (SET / GET)
    - core principles (ERROR, WARN, INFO, IGNORE)
    - stdlib validators/transformers

Examples:

    from stdlib.codex import IS_INT, POSITIVE, CLEAN_EMAIL

    class User:
        age = IS_INT + POSITIVE + IN_RANGE(0, 150)
        email = CLEAN_EMAIL
"""

from __future__ import annotations

from .stdlib_codex import StdCodex
from .phases import SET, GET
from .principles import ERROR
from .validators.numbers import is_int, positive, in_range
from .validators.email import require_at
from .validators.text import non_empty
from .transformers.email import normalize_email
from .transformers.text import strip, normalize
from .transformers.numbers import to_int


# ---------------------------------------------------------------
# Numeric Codex building blocks
# ---------------------------------------------------------------

# "value must be interpretable as int"
#
# Strategy:
#     - primary: is_int (fast check)
#     - fallback: to_int, then retry is_int
#
IS_INT = StdCodex(
    (SET >> is_int << to_int) @ ERROR,
)


# "value must be > 0" (assumes it is already numeric/int-like)
POSITIVE = StdCodex(
    (SET >> positive) @ ERROR,
)


def IN_RANGE(min_val=None, max_val=None) -> StdCodex:
    """
    Build a Codex that requires the value to be within [min_val, max_val].

    Example:
        AGE_RANGE = IN_RANGE(0, 150)

        class User:
            age = IS_INT + POSITIVE + AGE_RANGE
    """
    return StdCodex(
        (SET >> in_range(min_val, max_val)) @ ERROR,
)


# ---------------------------------------------------------------
# Text Codex building blocks
# ---------------------------------------------------------------

NON_EMPTY_STR = StdCodex(
    (SET >> strip >> non_empty) @ ERROR,
)

NORMALIZED_TEXT = StdCodex(
    (SET >> strip >> normalize) @ ERROR,
)


# ---------------------------------------------------------------
# Email Codex building blocks
# ---------------------------------------------------------------

CLEAN_EMAIL = StdCodex(
    (SET >> normalize_email >> require_at) @ ERROR,
    (GET >> normalize),
)
