from dsl import Section, StepToken, Relation
from codex.compiler.compile import compile_sections
from codex.ir.phase import Phase
from codex.ir.output import Output, RETURN, DROP
from codex.runtime.engine import Engine


def good(x):
    return f"val:{x}"


def bad(x):
    return ValueError("oops")


def test_output_routing_return_vs_drop_exception():
    # Section with two clusters; attach semantics to route values and exceptions.
    # - write (value) -> RETURN
    # - exc (exception) -> DROP (simulated via is_exception True)
    sec = Section(
        phase=Phase.SET,
        clusters=(
            (StepToken(good, Relation.PRIMARY),),
            (StepToken(bad, Relation.PRIMARY),),
        ),
        semantic=(Output(dest=RETURN), Output(is_exception=True, dest=DROP)),
    )

    plans = compile_sections((sec,))
    plan = plans[Phase.SET]
    eng = Engine()

    # Run engine to get final (result, is_exc)
    result, is_exc = eng.run(plan.pipeline, "X")

    # Routing policy: if is_exc, this would be dropped; else returned.
    # Here we assert the flags and value; actual descriptor routing lives elsewhere.
    assert is_exc is True
    assert isinstance(result, ValueError)
