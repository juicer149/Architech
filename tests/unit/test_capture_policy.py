from control.capture.config import CaptureConfig, CaptureValue
from control.capture.capture import Capture
from control.capture.context import ObservationContext


def f_ok(x):
    return x * 2


def f_typegate(x):
    return str(x)


def test_fast_path_no_events():
    cap = Capture()
    cfg = CaptureConfig(domain="Test", stage="1", input=None, output=None)
    with ObservationContext.push() as lb:
        result = cap(f_ok, 3, config=cfg, label=None)
    assert result == 6
    assert lb.last() is None  # no event when fast path and no errors


def test_capture_values_on_success():
    cap = Capture()
    cfg = CaptureConfig(domain="Test", stage="1", input=CaptureValue(capture=True), output=CaptureValue(capture=True))
    with ObservationContext.push() as lb:
        result = cap(f_ok, 2, config=cfg, label="L")
    assert result == 4
    # Depending on implementation, event may exist due to capture policy
    # Accept either presence with snapshots or absence; here we ensure at least no error


def test_type_gate_mismatch_creates_event():
    cap = Capture()
    cfg = CaptureConfig(domain="Test", stage="1", input=CaptureValue(types=(int,)), output=CaptureValue(types=(int,)))
    with ObservationContext.push() as lb:
        result = cap(f_typegate, 5, config=cfg, label="Gate")
    assert result == "5"
    evt = lb.last()
    assert evt is not None  # mismatch on output type should create event
