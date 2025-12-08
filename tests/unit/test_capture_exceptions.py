import pytest


def test_placeholder_capture_removed():
    # Capture layer removed; ensure module absence is expected
    with pytest.raises(ModuleNotFoundError):
        __import__("control.capture.capture")
