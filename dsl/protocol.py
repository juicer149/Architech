# ================================================================
# architech/dsl/protocol.py
# ================================================================
"""
Protocols describing what the DSL expects from backend phase keys
and callable step functions.

The DSL is intentionally generic and does not know about Codex semantics.
"""

from __future__ import annotations
from typing import Any, Callable, Protocol, runtime_checkable


@runtime_checkable
class DSLPhaseKey(Protocol):
    """
    Minimal interface representing a “phase”.

    Must support:
        - hashing
        - equality
        - stringification

    Backends (e.g. Codex) typically map SET/GET to enum values satisfying this.
    """
    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        ...

# thought:
# funderar krin om dsl ens behöver veta att detta är en callable per se
# alltså att detta ansvar hör till Codex backend?
# att det i DSL är en Any bara och att Codex backend ansvarar för att
# det är en callable som tar en input och ger en output?
StepFn = Callable[[Any], Any]
# ny:
# Step = Any # kanske även lägga denna i något som dsl/annotations.py?
