import pytest

from codex.models import section_from_dsl, _phase_from_key
from dsl import Section, Cluster, Relation, StepToken


def test_phase_from_key_invalid_string():
    with pytest.raises(ValueError):
        _phase_from_key("BAD")


def test_phase_from_key_invalid_type():
    with pytest.raises(TypeError):
        _phase_from_key(123)


def test_empty_cluster_raises():
    sec = Section(phase="SET", clusters=((),))
    with pytest.raises(ValueError):
        section_from_dsl(sec)


def test_mixed_relations_in_fallback_cluster_raises():
    tokens = (
        StepToken(Relation.PRIMARY, lambda x: x),
        StepToken(Relation.FALLBACK, lambda x: x),
        StepToken(Relation.OR, lambda x: x),
    )
    sec = Section(phase="SET", clusters=(tokens,))
    with pytest.raises(ValueError):
        section_from_dsl(sec)


def test_unexpected_relation_raises():
    class FakeRel:
        pass
    tokens = (
        StepToken(Relation.PRIMARY, lambda x: x),
        StepToken(FakeRel(), lambda x: x),
    )
    sec = Section(phase="SET", clusters=(tokens,))
    with pytest.raises(ValueError):
        section_from_dsl(sec)
