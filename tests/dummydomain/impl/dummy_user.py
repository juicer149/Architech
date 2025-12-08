"""
Dummy domain model used for integration testing of Codex + DSL + stdlib.
Model-only file: tests live under tests/full/.
"""

from __future__ import annotations

from dsl import PhaseTokenBase
from codex import Codex
from codex.models import Phase
from stdlib.codex import SET, WARN_P, INFO_P, IGNORE_P, StdCodex
from stdlib.codex.codex import IS_INT, POSITIVE, CLEAN_EMAIL
from stdlib.codex.validators.numbers import in_range
from stdlib.codex.validators.text import non_empty
from stdlib.codex.transformers.text import strip, normalize


class DummyUser:
    NAME_SET = PhaseTokenBase(Phase.SET)
    NAME_GET = PhaseTokenBase(Phase.GET)

    name = Codex(
        NAME_SET >> strip >> non_empty | WARN_P,
        NAME_GET >> normalize | INFO_P,
        strict=None,
        default="",
    )

    age = IS_INT + POSITIVE

    score = StdCodex(
        SET >> in_range(0, 100) | IGNORE_P
    )

    email = CLEAN_EMAIL

    def _primary_fail(x):
        return ValueError("primary failed")

    def _fallback_ok(x):
        return str(x) + "_fixed"

    FALL_SET = PhaseTokenBase(Phase.SET)
    fallback_field = Codex(
        FALL_SET >> _primary_fail << _fallback_ok | WARN_P,
        strict=False,
    )

    def __init__(self, name="", age=None, score=None, email=None, fallback_field=None):
        if name:
            self.name = name
        if age is not None:
            self.age = age
        if score is not None:
            self.score = score
        if email is not None:
            self.email = email
        if fallback_field is not None:
            self.fallback_field = fallback_field
