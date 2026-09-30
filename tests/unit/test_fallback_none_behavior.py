from dsl import Section, StepToken, Relation
from codex.compiler.compile import compile_sections
from codex.ir.phase import Phase
from codex.runtime.engine import Engine


def primary_after_fix(x):
    # before fix: fail; after fix: None to keep current
    if x == "fixed":
        return None
    return ValueError("bad input")


def fix_to_none(x):
    # fallback fixes input to a value that causes primary to return None
    # Engine should treat None as pass-through (keep current)
    return "fixed"


def primary_none(x):
    # primary returns None -> pass-through of current
    return None


def test_fallback_then_primary_none_passes_through_current():
    # Cluster: PRIMARY (fails semantically) + FALLBACK (produces fixed) then PRIMARY(None)
    # Build as two clusters to express fallback then subsequent primary-none behavior.
    sec = Section(
        phase=Phase.SET,
        clusters=(
            (
                StepToken(primary_after_fix, Relation.PRIMARY),
                StepToken(fix_to_none, Relation.FALLBACK),
            ),
            (
                StepToken(primary_none, Relation.PRIMARY),
            ),
        ),
        semantic=None,
    )

    plans = compile_sections((sec,))
    plan = plans[Phase.SET]

    eng = Engine()
    result, is_exc = eng.run(plan.pipeline, "raw")
    # After fallback fixes to "fixed", next PRIMARY returns None -> pass-through
    assert is_exc is False
    assert result == "fixed"
