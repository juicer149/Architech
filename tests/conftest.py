# tests/conftest.py

import pytest
from control.panopticon import Panopticon
from control.capture.capture import Capture

@pytest.fixture
def pan():
    return Panopticon(capture=Capture())
