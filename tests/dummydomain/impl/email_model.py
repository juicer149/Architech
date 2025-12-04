# tests/dummydomain/impl/email_model.py

from blueprint.codex import Codex, SET, GET
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
    address = Codex(
        # SET is strict → pure Python validation, no Panopticon
        SET(strict=True) >> to_str >> strip >> require_at | EMAIL_ERROR,
        # GET is interpreted → Panopticon captures + WARN printed
        GET(strict=False) >> lowercase | EMAIL_WARN,
        strict=None,
    ) 

    def __init__(self, addr):
        self.address = addr
