"""Steps may raise instead of return; severity still decides the outcome."""
import pytest

from stdlib.codex import StdCodex, SET, ERROR, WARN


def raises_on_digits(v):
    if any(c.isdigit() for c in v):
        raise ValueError(f"digits not allowed: {v!r}")
    return v


def int_or_raise(v):
    return int(v)            # raises ValueError on "2.7"


def floor_float(v):
    return str(int(float(v)))


class Model:
    strict = StdCodex(SET >> raises_on_digits)
    error = StdCodex((SET >> raises_on_digits) @ ERROR)
    warn = StdCodex((SET >> raises_on_digits) @ WARN, default="")
    repaired = StdCodex(SET >> int_or_raise << floor_float)
    either = StdCodex(SET >> int_or_raise | floor_float)


def test_strict_mode_reraises_the_original_exception():
    m = Model()
    with pytest.raises(ValueError, match="digits not allowed"):
        m.strict = "R2D2"


def test_raised_exception_respects_error_severity():
    m = Model()
    m.error = "Ada"
    with pytest.raises(RuntimeError, match=r"\[error\] digits not allowed"):
        m.error = "R2D2"
    assert m.error == "Ada"


def test_raised_exception_respects_warn_severity(capsys):
    m = Model()
    m.warn = "R2D2"
    assert "[warn] digits not allowed" in capsys.readouterr().out


def test_raised_exception_triggers_fallback():
    m = Model()
    m.repaired = "2.7"
    assert m.repaired == 2


def test_raised_exception_triggers_alternative():
    m = Model()
    m.either = "2.7"
    assert m.either == "2"


def test_keyboard_interrupt_is_never_swallowed():
    def interrupt(v):
        raise KeyboardInterrupt

    class M:
        x = StdCodex((SET >> interrupt) @ WARN)

    with pytest.raises(KeyboardInterrupt):
        M().x = "a"
