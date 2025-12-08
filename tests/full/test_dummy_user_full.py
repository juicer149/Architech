import pytest

from tests.dummydomain.impl.dummy_user import DummyUser
from dsl import PhaseTokenBase
from codex import Codex
from codex.models import Phase
from stdlib.codex import ERROR
from stdlib.codex.validators.email import require_at
from stdlib.codex.transformers.text import strip, normalize


def test_name_normalization_and_warn_full():
    u = DummyUser(name="  Alice  ")
    assert u.name == "alice"
    u.name = "   Bob   "
    assert u.name == "bob"


def test_age_int_and_positive_full():
    u = DummyUser(age="10")
    assert u.age == 10
    with pytest.raises(RuntimeError):
        u.age = -5


def test_score_ignore_semantics_full():
    u = DummyUser(score=-10)
    assert u.score == -10
    u.score = 200
    assert u.score == 200


def test_email_cleaning_and_error_full():
    u = DummyUser(email="  TEST@Example.com ")
    assert u.email == "test@example.com"
    with pytest.raises(RuntimeError):
        u.email = "invalid"


def test_fallback_mechanism_full():
    u = DummyUser(fallback_field="abc")
    assert u.fallback_field == "abc_fixed"


def test_strict_mode_disallows_semantics_full():
    STRICT_SET = PhaseTokenBase(Phase.SET)
    c = Codex(STRICT_SET >> require_at | ERROR, strict=True)

    class X:
        field = c

        def __init__(self, v):
            self.field = v

    with pytest.raises(ValueError):
        X("no-at")


def test_auto_semantic_mode_full():
    AUTO_SET = PhaseTokenBase(Phase.SET)
    c = Codex(AUTO_SET >> require_at | ERROR)

    class X:
        field = c

    with pytest.raises(RuntimeError):
        X("invalid")


def test_get_pipeline_is_respected_full():
    u = DummyUser(name="  Foo  ")
    assert u.name == "foo"


def test_raw_stepchain_flow_full():
    SETT = PhaseTokenBase(Phase.SET)
    chain = (SETT >> strip >> normalize) | ERROR
    section = chain.to_section()
    assert section.phase == Phase.SET
    assert len(section.clusters) == 2
    spec = Codex(chain)._get_engine().spec
    assert Phase.SET in spec.phases
