# ================================================================
# control/semantics/codex_semantics.py
# ================================================================
"""
Semantic vocabulary and normalization utilities for Codex.

Provides:

    • Predefined semantic constants:
          ERROR, WARN, IGNORE, CRITICAL, INFO

    • A normalization function:
          to_principle(obj) → Principle

The Codex DSL layer uses these via:

    SET >> f | token
"""

from __future__ import annotations

from typing import Any

from control.config import Principle, Praxis, Effect
from blueprint.codex.constants import (
    DEFAULT_LABEL,
    DEFAULT_PRAXIS,
    DEFAULT_EFFECT,
)


# ---------------------------------------------------------------------------
# Predefined semantic vocabulary
# ---------------------------------------------------------------------------

ERROR = Principle("error", DEFAULT_PRAXIS, Effect.RAISE)
FATAL = Principle("fatal", Praxis.IMMEDIATE, Effect.RAISE)
WARN = Principle("warn", Praxis.DEFER, Effect.PRINT)
IGNORE = Principle("ignore", Praxis.IGNORE, Effect.NONE)
CRITICAL = Principle("critical", Praxis.DEFER, Effect.RAISE)
INFO = Principle("info", Praxis.DEFER, Effect.PRINT)

_PREDEFINED_BY_NAME = {
    "error": ERROR,
    "fatal": FATAL,
    "warn": WARN,
    "warning": WARN,
    "ignore": IGNORE,
    "critical": CRITICAL,
    "info": INFO,
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _from_str(label: str) -> Principle:
    key = label.lower().strip()
    if key in _PREDEFINED_BY_NAME:
        return _PREDEFINED_BY_NAME[key]
    return Principle(key, DEFAULT_PRAXIS, DEFAULT_EFFECT)


def _from_bool(flag: bool) -> Principle:
    praxis = Praxis.IMMEDIATE if flag else Praxis.NONE
    return Principle(DEFAULT_LABEL, praxis, DEFAULT_EFFECT)


def _from_praxis(p: Praxis) -> Principle:
    return Principle(DEFAULT_LABEL, p, DEFAULT_EFFECT)


def _from_effect(e: Effect) -> Principle:
    return Principle(DEFAULT_LABEL, DEFAULT_PRAXIS, e)


def _normalize_praxis(x: Any) -> Praxis:
    if isinstance(x, Praxis):
        return x
    if isinstance(x, bool):
        return Praxis.IMMEDIATE if x else Praxis.NONE
    raise TypeError(f"Invalid praxis token: {x!r}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def to_principle(obj: Any) -> Principle:
    match obj:
        case (x,):
            return to_principle(x)
        case (label, praxis_raw):
            praxis = _normalize_praxis(praxis_raw)
            return Principle(str(label), praxis, DEFAULT_EFFECT)
        case (label, praxis_raw, exc_type):
            praxis = _normalize_praxis(praxis_raw)
            if not isinstance(exc_type, type) or not issubclass(exc_type, BaseException):
                raise TypeError(f"Invalid exception type: {exc_type!r}")
            return Principle(  # type: ignore[call-arg]
                str(label),
                praxis,
                DEFAULT_EFFECT,
                exc_type=exc_type,  # type: ignore[call-arg]
            )
        case tuple():
            raise TypeError(f"Invalid semantic tuple: {obj!r}")

    if isinstance(obj, Principle):
        return obj
    if isinstance(obj, Praxis):
        return _from_praxis(obj)
    if isinstance(obj, Effect):
        return _from_effect(obj)
    if isinstance(obj, bool):
        return _from_bool(obj)
    if isinstance(obj, str):
        return _from_str(obj)
    if obj is None:
        return Principle(DEFAULT_LABEL, DEFAULT_PRAXIS, DEFAULT_EFFECT)
    raise TypeError(f"Cannot convert {obj!r} into a Principle")


__all__ = [
    "ERROR",
    "FATAL",
    "WARN",
    "IGNORE",
    "CRITICAL",
    "INFO",
    "to_principle",
]
