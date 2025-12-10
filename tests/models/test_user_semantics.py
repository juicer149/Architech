import pytest

from tests.models.user import User, NAME_RULES, AGE_RULES, EMAIL_RULES
from stdlib.codex import SET, GET


def test_name_set_strip_and_non_empty_warn():
    u = User(name="   Alice   ")
    # SET phase applied on assignment; strip + non_empty
    # GET normalization to lowercase applies on access
    assert u.name == "alice"

    # Empty after strip triggers WARN (should not raise, rule keeps default)
    u = User(name="   ")
    # When WARN triggers on non_empty, stdlib keeps the descriptor default
    # StdCodex stores this as _default on the descriptor
    assert hasattr(NAME_RULES, "_default")
    assert u.name == getattr(NAME_RULES, "_default")


def test_name_get_normalize_info():
    u = User(name="  Alice " )
    # GET phase via descriptor access (assumes stdlib Codex behavior)
    val = u.name
    assert val == "alice"  # normalized to lowercase


def test_age_composed_rules_positive_in_range():
    u = User(age=25)
    assert u.age == 25

    # Negative -> violation; expect keeping current value or applying default
    with pytest.raises(Exception):
        User(age=-3)

    # Out of range
    with pytest.raises(Exception):
        User(age=999)


def test_email_cleaner_applies():
    u = User(email="  Foo@Bar.Com  ")
    # CLEAN_EMAIL likely strips and normalizes case and format
    assert "@" in u.email
    assert u.email == u.email.strip()
