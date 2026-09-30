from dsl import Section, Relation, StepToken
from codex.ir.phase import Phase
from codex.ir.semantics import Principle
from codex.compiler.compile import compile_sections


def test_principle_normalized_from_string_in_compiler():
    sec = Section(
        phase=Phase.GET,
        clusters=((StepToken(lambda x: x, Relation.PRIMARY),),),
        semantic="warn",
    )
    plans = compile_sections((sec,))
    plan = plans[Phase.GET]
    assert isinstance(plan.principle, Principle)
    assert plan.principle.label == "warn"
