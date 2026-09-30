from typing import Any

from dsl import Section, StepToken, Relation
from codex.ir.phase import Phase
from codex.ir.semantics import Principle, Praxis
from codex.compiler.compile import compile_sections


def idfn(x: Any) -> Any:
    return x


def test_compile_single_set_phase_with_principle():
    sec = Section(
        phase=Phase.SET,
        clusters=((StepToken(idfn, Relation.PRIMARY),),),
        semantic=Principle("error", Praxis()),
    )

    plans = compile_sections((sec,))
    assert Phase.SET in plans and Phase.GET not in plans
    plan = plans[Phase.SET]
    assert plan.principle is not None
    assert isinstance(plan.principle, Principle)
    assert plan.principle.label == "error"


def test_compile_single_get_phase_without_principle():
    sec = Section(
        phase=Phase.GET,
        clusters=((StepToken(idfn, Relation.PRIMARY),),),
        semantic=None,
    )

    plans = compile_sections((sec,))
    assert Phase.GET in plans and Phase.SET not in plans
    plan = plans[Phase.GET]
    assert plan.principle is None
