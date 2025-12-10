# ================================================================
# tests/end_to_end/test_user_model.py
# ================================================================

from __future__ import annotations

import pytest

from tests.models.user import User


def test_user_name_set_and_get():
    u = User()
    u.name = "   Alice   "

    # SET: strip + non_empty (WARN)
    # GET: normalize (INFO)
    assert u.name == "alice"


def test_user_name_warn_on_empty_but_not_crash():
    u = User()
    # Empty after strip: should trigger WARN principle but not block assignment
    u.name = "   "
    # GET: normalize("") → still ""
    assert u.name == ""


def test_user_age_full_pipeline_success():
    u = User()
    u.age = "42"   # will convert to int via IS_INT fallback

    assert u.age == 42


def test_user_age_invalid_negative():
    u = User()

    # POSITIVE @ ERROR → raise
    with pytest.raises(Exception):
        u.age = -5


def test_user_age_invalid_range():
    u = User()

    # IN_RANGE(0, 150) @ ERROR → raise
    with pytest.raises(Exception):
        u.age = 500


def test_user_email_normalization():
    u = User()
    u.email = "   TEST@EXAMPLE.com  "

    # SET: normalize_email -> "test@example.com"
    # GET: normalize (lowercase, already normalized)
    assert u.email == "test@example.com"


def test_user_email_missing_at():
    u = User()
    with pytest.raises(Exception):
        u.email = "not-an-email"
