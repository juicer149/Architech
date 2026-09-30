# tests/models/user.py
from __future__ import annotations

from typing import Any

from dsl import PhaseToken
from codex import Codex
from codex.ir.phase import Phase
from codex.lang import ERROR, WRITE_SELF, WRITE_RETURN

# ------------------------------------------------------------
# Phase tokens (user-facing DSL)
# ------------------------------------------------------------

SET = PhaseToken(Phase.SET)
GET = PhaseToken(Phase.GET)

# ------------------------------------------------------------
# Step functions (pure, boring, explicit)
# ------------------------------------------------------------

def strip(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value

def non_empty(value: Any) -> Any:
    if value == "":
        return ValueError("empty string not allowed")
    return value

def to_lower(value: Any) -> Any:
    if isinstance(value, str):
        return value.lower()
    return value

def must_be_int(value: Any) -> Any:
    if isinstance(value, int):
        return value
    return ValueError("not an int")

# ------------------------------------------------------------
# Codex pipelines
# ------------------------------------------------------------

NAME = Codex(
    # SET: strip + require non-empty
    (SET >> strip >> non_empty) @ ERROR,
    # GET: normalize
    (GET >> to_lower),
)

AGE = Codex(
    (SET >> must_be_int) @ ERROR,
)

# ------------------------------------------------------------
# Model
# ------------------------------------------------------------

class User:
    name = NAME
    age = AGE

    def __init__(self, *, name=None, age=None):
        if name is not None:
            self.name = name
        if age is not None:
            self.age = age
