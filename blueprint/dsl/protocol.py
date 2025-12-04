# ================================================================
# blueprint/dsl/protocol.py
# ================================================================
"""
Protocols (ABCs) that describe what the DSL expects from a Phase token
and from a callable step function.

These protocols let Codex define SET/GET *outside* the DSL while still
letting StepChain operate generically.
"""

from __future__ import annotations

from typing import Protocol, Any, Hashable

# NOTE:
# This import is for typing only and does NOT create cycles.
# If syntax is not yet available during type checking/build, fall back.
try:
    from .syntax import StepChain  # type: ignore[typing-only]
except Exception:
    StepChain = object  # type: ignore[assignment]


class CallableLike(Protocol):
    """Any runtime object that behaves like a transform function."""
    def __call__(self, value: Any) -> Any:
        ...


class DSLPhaseKey(Hashable, Protocol):
    """
    A lightweight, hashable marker describing the phase identifier.

    Codex will implement this via enums (SET/GET), and Enum already satisfies
    Hashable — so we do NOT constrain __eq__/__repr__ signatures to avoid
    mypy warnings with Enum's positional-only params.
    """
    ...


class PhaseTokenLike(Protocol):
    """
    Interface used by StepChain's entry point in syntax.

    Codex supplies concrete PhaseToken implementations that conform.
    """

    phase_key: DSLPhaseKey
    phase_kwargs: dict[str, Any]

    def with_overrides(self, **kwargs: Any) -> "PhaseTokenLike": ...
    def start_chain(self, fn: CallableLike) -> Any: ...
