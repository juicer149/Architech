import pytest
from dataclasses import dataclass, FrozenInstanceError

from codex import Codex


def test_frozen_dataclass_init_sets_codex_field():
    @dataclass(frozen=True)
    class X:
        email: str = Codex()

    x = X("a@b.com")
    assert x.email == "a@b.com"


def test_frozen_dataclass_assignment_raises():
    @dataclass(frozen=True)
    class X:
        email: str = Codex()

    x = X("a@b.com")
    with pytest.raises(FrozenInstanceError):
        x.email = "b@b.com"
