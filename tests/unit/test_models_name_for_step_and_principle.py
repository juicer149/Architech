from codex.models import section_from_dsl
from dsl import Section, Relation, StepToken
from codex.semantics import Principle


def test_name_for_step_lambda_repr_used():
    lam = lambda x: x  # lambda has __name__ = '<lambda>' but repr is acceptable
    sec = Section(
        phase="SET",
        clusters=((StepToken(lam, Relation.PRIMARY),),),
        semantic=None,
    )
    spec = section_from_dsl(sec)
    # Ensure the primary_name is populated; either '__name__' or repr
    assert spec.clusters[0].primary_name in (getattr(lam, "__name__", None), repr(lam))


def test_section_principle_normalized_from_string():
    sec = Section(
        phase="GET",
        clusters=((StepToken(lambda x: x, Relation.PRIMARY),),),
        semantic="warn",
    )
    spec = section_from_dsl(sec)
    assert isinstance(spec.principle, Principle)
    assert spec.principle.label == "warn"
