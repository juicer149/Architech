# ================================================================
# architech/dsl/protocol.py
# ================================================================
"""
Protocols and type aliases describing what the DSL expects from
backend phase keys and step objects.

The DSL itself is intentionally generic and does not know about Codex
or any other backend semantics. It only assumes:

    - there is some notion of a *phase key*
    - steps are opaque objects that backends know how to interpret

Backends are free to map these abstractions onto enums, callables,
data classes, or any other internal representations.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class DSLPhaseKey(Protocol):
    """
    Minimal interface representing a “phase”.

    Must support:

        - hashing
        - equality
        - stringification

    Backends (e.g. Codex) typically map SET/GET to enum values
    satisfying this protocol.
    """

    def __str__(self) -> str:  # pragma: no cover - protocol stub
        ...

    def __repr__(self) -> str:  # pragma: no cover - protocol stub
        ...


# In the generic DSL, a “step” is just an opaque object that the
# backend understands. It does *not* have to be callable.
#
# For Codex, the natural choice is a unary callable, but the
# core DSL does not enforce that.
Step = Any
