from control.capture.capture import Capture
from control.capture.config import CaptureConfig
from control.capture.context import ObservationContext
from tests.dummydomain.impl.errors import raise_error


def test_event_on_exception_fast_path():
    cap = Capture()
    cfg = CaptureConfig(domain="X", stage="1")  # fast path
    with ObservationContext.push() as lb:
        try:
            cap(raise_error, 0, config=cfg, label="boom")
        except ValueError:
            pass
    evt = lb.last()
    assert evt is not None
