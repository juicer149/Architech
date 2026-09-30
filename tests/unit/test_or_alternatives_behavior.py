from dsl import Section, StepToken, Relation
from codex.compiler.compile import compile_sections
from codex.ir.phase import Phase
from codex.runtime.engine import Engine


def fail_exc(x):
    # return an exception object = semantic failure
    return ValueError("primary failed")


def alt_success(x):
    # alternative succeeds; returns transformed value
    return f"ok:{x}"


def test_or_semantic_replay_first_success_wins():
    # Strict pass: primary returns exception -> aborts strict
    # Semantic replay: try primary, then OR; OR succeeds -> final value
    sec = Section(
        phase=Phase.SET,
        clusters=((
            StepToken(fail_exc, Relation.PRIMARY),
            StepToken(alt_success, Relation.OR),
        ),),
        semantic=None,
    )
    plans = compile_sections((sec,))
    plan = plans[Phase.SET]

    eng = Engine()
    result, is_exc = eng.run(plan.pipeline, "X")
    assert is_exc is False
    assert result == "ok:X"
