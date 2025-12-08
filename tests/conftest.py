# tests/conftest.py

import pytest

def make_capture():
    # Control/capture layer removed in new design.
    # Provide a no-op factory for tests that referenced capture.
    return None
