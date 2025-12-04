# ================================================================
# architech/control/effect/__init__.py
# ================================================================
"""
Effect package — formatting and surfacing of semantic events.

This package encapsulates how semantic Events are:

    1. Rendered into text (formatter layer)
    2. Surfaced via side-effects (executor layer)

Panopticon does *not* talk directly to formatters or executors. Instead,
it calls the EffectExe facade, which chooses a formatter and an executor
based on logical keys (effect key, style).

Public surface
--------------

- EffectExe:
    Static facade used by Panopticon to realize effects
    (format events → execute effect).

Formatter layer
---------------

- DeferredEvents:
    Type alias for Iterable[(Principle, Event)].

- Formatter:
    Callable type for formatter functions.

- register_formatter(name, formatter):
    Register a named formatter implementation.

- get_formatter(name) -> Formatter | None:
    Lookup a formatter by name.

- pretty_formatter:
    Built-in multiline human-friendly formatter.

Executor layer
--------------

- Executor:
    Callable type for effect executors.

- register_executor(mode, executor):
    Register a named executor implementation.

- get_executor(mode) -> Executor | None:
    Lookup an executor by mode.

- eff_print:
    Built-in executor that prints the text to stdout.

- eff_raise:
    Built-in executor that raises RuntimeError with the text as message.
"""

from __future__ import annotations

from .effect import EffectExe
from .formatter import (
    DeferredEvents,
    Formatter,
    register_formatter,
    get_formatter,
    pretty_formatter,
)
from .executor import (
    Executor,
    register_executor,
    get_executor,
    eff_print,
    eff_raise,
)

__all__ = [
    # Facade
    "EffectExe",
    # Formatter layer
    "DeferredEvents",
    "Formatter",
    "register_formatter",
    "get_formatter",
    "pretty_formatter",
    # Executor layer
    "Executor",
    "register_executor",
    "get_executor",
    "eff_print",
    "eff_raise",
]
