from dsl import Section, StepToken, Relation
from codex.compiler.compile import compile_sections
from codex.ir.phase import Phase
from codex.runtime.engine import Engine


def hard_raise(x):
    raise RuntimeError("hard")


def soft_fail(x):
    # succeed if fixed value provided, else semantic failure
    if x == "fixed":
        return x  # success path
    return ValueError("soft")


def fix_ok(x):
    return "fixed"


def test_strict_aborts_on_hard_exception():
    # Strict pass: hard exception should abort immediately; engine returns (exc, True)
    sec = Section(
        phase=Phase.SET,
        clusters=((StepToken(hard_raise, Relation.PRIMARY),),),
        semantic=None,
    )
    plans = compile_sections((sec,))
    plan = plans[Phase.SET]
    eng = Engine()
    result, is_exc = eng.run(plan.pipeline, "X")
    assert is_exc is True
    assert isinstance(result, RuntimeError)


def test_semantic_replay_recovers_via_fallback():
    # Strict pass: soft_fail returns exception -> fails strict, not raised
    # Semantic replay: use FALLBACK to produce a value; primary does not run again
    # Final: recovered value and not exception.
    sec = Section(
        phase=Phase.SET,
        clusters=(
            (
                StepToken(soft_fail, Relation.PRIMARY),
                StepToken(fix_ok, Relation.FALLBACK),
            ),
        ),
        semantic=None,
    )
    plans = compile_sections((sec,))
    plan = plans[Phase.SET]
    eng = Engine()
    result, is_exc = eng.run(plan.pipeline, "Z")
    assert is_exc is False
    assert result == "fixed"
