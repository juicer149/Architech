from dsl import Section, StepToken, Relation
from codex.compiler.compile import compile_sections
from codex.ir.phase import Phase
from codex.runtime.engine import Engine


def strip(x: str) -> str:
    return x.strip()


def to_lower(x: str):
    return x.lower()


def test_engine_runs_compiled_pipeline_simple_set():
    sec = Section(
        phase=Phase.SET,
        clusters=((StepToken(strip, Relation.PRIMARY),), (StepToken(to_lower, Relation.PRIMARY),)),
        semantic=None,
    )
    plans = compile_sections((sec,))
    plan = plans[Phase.SET]

    eng = Engine()
    result, is_exc = eng.run(plan.pipeline, "  Alice  ")

    assert is_exc is False
    assert result == "alice"
