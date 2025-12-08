# tests/dummydomain/impl/email_model.py

from dsl import PhaseTokenBase
from codex import Codex
from codex.models import Phase
from tests.dummydomain.semantics import EMAIL_ERROR, EMAIL_WARN


# --- Pipeline helpers ---

def to_str(v):
    return str(v)

def strip(v):
    return v.strip()

def require_at(v):
    if "@" not in v:
        return ValueError("missing @")
    return v

def lowercase(v):
    return v.lower()


# --- Dummy model using Codex ---

class Email:
    # Phase tokens bound to Codex Phase enum
    _SET = PhaseTokenBase(Phase.SET)
    _GET = PhaseTokenBase(Phase.GET)

    address = Codex(
        _SET >> to_str >> strip >> require_at | EMAIL_ERROR,
        _GET >> lowercase | EMAIL_WARN,
        strict=None,
    )

    def __init__(self, addr):
        self.address = addr
