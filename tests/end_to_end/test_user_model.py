# tests/end_to_end/test_user_model.py
from __future__ import annotations

import pytest

from tests.models.user import User

# ------------------------------------------------------------
# NAME
# ------------------------------------------------------------

def test_name_set_and_get():
    u = User(name="  Alice  ")

    # SET: strip + non_empty
    # GET: to_lower
    assert u.name == "alice"


def test_name_empty_raises():
    u = User()

    with pytest.raises(ValueError):
        u.name = "   "


def test_name_get_does_not_mutate_storage():
    u = User()
    u.name = "Bob"

    # stored value should be original SET result
    assert u.__dict__["name"] == "Bob"

    # GET applies transformation
    assert u.name == "bob"

# ------------------------------------------------------------
# AGE
# ------------------------------------------------------------

def test_age_accepts_int():
    u = User(age=42)
    assert u.age == 42


def test_age_rejects_non_int():
    u = User()

    with pytest.raises(ValueError):
        u.age = "42"
