# ================================================================
# tests/unit/test_user_rules.py
# ================================================================
"""
Unit-level tests for the stdlib Codex pipelines used in User.

These tests exercise the Codex rules directly, without going through
the User descriptor, to make debugging easier if something breaks in
the engine or stdlib.
"""

from __future__ import annotations

import pytest

from tests.models.user import NAME_RULES, AGE_RULES, EMAIL_RULES
from codex.models import Phase


def run_get(rule, value):
    eng = rule._get_engine()
    return eng.run_phase(Phase.GET, value)


def run_set(rule, value):
    eng = rule._get_engine()
    return eng.run_phase(Phase.SET, value)


# ----------------------------- NAME -----------------------------

def test_name_strip_and_warn():
    r = NAME_RULES

    out = run_set(r, "  Bob  ")
    # SET: strip + non_empty
    assert out == "Bob"

    # GET: normalize → "bob"
    assert run_get(r, out) == "bob"


def test_name_empty_triggers_warn_not_error():
    r = NAME_RULES

    # Should not raise in semantic WARN mode; just record violation
    out = run_set(r, "   ")
    # Non-empty validator fails → WARN, but value passes through as ""
    assert out == ""


# ------------------------------ AGE -----------------------------

def test_age_is_int_fallback():
    r = AGE_RULES
    out = run_set(r, "10")  # IS_INT: is_int + to_int
    assert out == 10


def test_age_positive_error():
    r = AGE_RULES
    with pytest.raises(Exception):
        run_set(r, -1)


def test_age_range_error():
    r = AGE_RULES
    with pytest.raises(Exception):
        run_set(r, 1000)


# ----------------------------- EMAIL ----------------------------

def test_email_normalization_and_validation():
    r = EMAIL_RULES
    out = run_set(r, "  Foo@BAR.com  ")
    assert out == "foo@bar.com"  # normalized by SET

    # GET normalize: should still be lowercase
    assert run_get(r, out) == "foo@bar.com"


def test_email_failure():
    r = EMAIL_RULES
    with pytest.raises(Exception):
        run_set(r, "invalid")
