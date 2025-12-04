from control.capture.config import CaptureValue, CaptureConfig
from control.capture.capture import Capture
from control.capture.context import ObservationContext


def f(x: int) -> int:
    return x


def test_input_type_gate_violation_creates_event():
    cap = Capture()
    cfg = CaptureConfig(domain="D.x", stage="1", input=CaptureValue(types=(int,)))
    with ObservationContext.push() as lb:
        _ = cap(f, "3", config=cfg, label="Gate")
    evt = lb.last()
    assert evt is not None

