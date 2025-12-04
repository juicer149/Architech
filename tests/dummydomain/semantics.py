# tests/dummydomain/semantics.py

from control.config import Principle, Praxis, Effect

EMAIL_ERROR = Principle(
    label="email_error",
    praxis=Praxis.IMMEDIATE,
    effect=Effect.RAISE,
    exc_type=ValueError,   # test that custom exception propagation works
)

EMAIL_WARN = Principle(
    label="email_warn",
    praxis=Praxis.DEFER,
    effect=Effect.PRINT,
)
