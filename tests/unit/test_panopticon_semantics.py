from control.panopticon import Panopticon
from control.capture.capture import Capture
from control.config import Principle, Praxis, Effect, SemanticInstruction
from control.capture.context import ObservationContext


def test_defer_and_immediate_effects(capsys):
    pan = Panopticon(capture=Capture())

    def ok(x):
        return x

    # IMMEDIATE PRINT
    p_print = Principle(label="print-now", praxis=Praxis.IMMEDIATE, effect=Effect.PRINT)
    with pan as px:
        call = px.observe(p_print, domain="D", stage="S")
        _ = call(ok, 1)
    # printed immediately

    # DEFER PRINT
    p_defer = Principle(label="print-later", praxis=Praxis.DEFER, effect=Effect.PRINT)
    with pan as px:
        call = px.observe(p_defer, domain="D", stage="S")
        _ = call(ok, 2)
    # flushed on exit

    # RAISE on exit — generate a real event via exception
    def bad(_):
        raise RuntimeError("fail")
    p_raise = Principle(label="raise", praxis=Praxis.DEFER, effect=Effect.RAISE)
    try:
        with pan as px:
            call = px.observe(p_raise, domain="D", stage="S")
            _ = call(bad, 3)
    except RuntimeError:
        # Panopticon defer will flush RAISE last on exit
        pass
