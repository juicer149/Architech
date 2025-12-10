# ================================================================
# tests/models/user.py
# ================================================================

from __future__ import annotations

from stdlib.codex import (
    StdCodex,
    SET,
    GET,
    ERROR,
    WARN,
    INFO,
    IS_INT,
    POSITIVE,
    IN_RANGE,
    CLEAN_EMAIL,
)
from stdlib.codex.validators.text import non_empty
from stdlib.codex.transformers.text import strip, normalize


# ---------------------------------------------------------------
# User.name rules
# ---------------------------------------------------------------
#
# - SET: strip whitespace, require non-empty (WARN-level)
# - GET: normalize to lowercase (INFO-level)
#
NAME_RULES = StdCodex(
    (SET >> strip >> non_empty) @ WARN,
    (GET >> normalize) @ INFO,
    default="",
)


# ---------------------------------------------------------------
# User.age rules
# ---------------------------------------------------------------
#
# - Must be int-like         (IS_INT)
# - Must be positive         (POSITIVE)
# - Must be within range     (0–150)
#
# We compose existing stdlib Codex pipelines instead of nesting them
# as steps. The __add__ on Codex merges sections.
#
AGE_RULES = IS_INT + POSITIVE + IN_RANGE(0, 150)


# ---------------------------------------------------------------
# User.email rules
# ---------------------------------------------------------------
EMAIL_RULES = CLEAN_EMAIL


# ---------------------------------------------------------------
# User model
# ---------------------------------------------------------------
class User:
    name = NAME_RULES
    age = AGE_RULES
    email = EMAIL_RULES

    def __init__(self, name=None, age=None, email=None):
        if name is not None:
            self.name = name
        if age is not None:
            self.age = age
        if email is not None:
            self.email = email
