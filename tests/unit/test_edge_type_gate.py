import pytest


def f(x: int) -> int:
    return x


def test_capture_stack_removed():
    with pytest.raises(ModuleNotFoundError):
        __import__("control.capture.context")

