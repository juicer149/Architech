import pytest


def f_ok(x):
    return x * 2


def f_typegate(x):
    return str(x)


def test_capture_layer_removed():
    with pytest.raises(ModuleNotFoundError):
        __import__("control.capture.config")


def test_capture_imports_fail():
    with pytest.raises(ModuleNotFoundError):
        __import__("control.capture.capture")


def test_capture_context_removed():
    with pytest.raises(ModuleNotFoundError):
        __import__("control.capture.context")
