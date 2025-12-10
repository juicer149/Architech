import pytest

from codex.semantics import normalize_principle, Principle


def test_normalize_none():
    assert normalize_principle(None) is None


def test_normalize_string_creates_principle():
    p = normalize_principle("warn")
    assert isinstance(p, Principle)
    assert p.label == "warn"


def test_normalize_bad_type_raises():
    with pytest.raises(TypeError):
        normalize_principle(object())
