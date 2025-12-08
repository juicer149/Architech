# tests/dummydomain/semantics.py

from codex.semantics import Principle, Praxis

EMAIL_ERROR = Principle("email_error", Praxis(True, True), exc_type=ValueError)
EMAIL_WARN = Principle("email_warn", Praxis(False, False))

