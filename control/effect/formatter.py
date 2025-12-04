# ================================================================
# architech/control/effect/formatter.py
# ================================================================
"""
Formatter registry for semantic events.

This module is responsible for turning *events* into *text*.

Concepts
--------
- DeferredEvents:
    Iterable of (Principle, Event) pairs. This is the semantic view
    of what happened during execution, as seen by the control layer.

- Formatter:
    Callable that renders DeferredEvents into a string. Different
    formatters can be used for different consumers (humans, logs,
    machines, etc.).

Registry
--------
- register_formatter(name, formatter):
    Register a named formatter implementation.

- get_formatter(name) -> Formatter | None:
    Lookup a formatter by name (case-insensitive).

Built-ins
---------
- pretty_formatter:
    Human-friendly multiline dump, equivalent to the original textual
    layout that used to live in Panopticon.
"""

from __future__ import annotations

from typing import Callable, Dict, Iterable, Optional, Tuple

from control.config import Principle
from control.capture.models import Event


# --------------------------------------------------------------------
# Types
# --------------------------------------------------------------------

DeferredEvents = Iterable[Tuple[Principle, Event]]
Formatter = Callable[[DeferredEvents], str]

# --------------------------------------------------------------------
# Registry
# --------------------------------------------------------------------

_FORMATTERS: Dict[str, Formatter] = {}


def register_formatter(name: str, formatter: Formatter) -> None:
    """
    Register a formatter under a logical name.

    Parameters
    ----------
    name:
        Logical key (e.g. "pretty", "json", "compact").
        The name is lowercased before insertion.

    formatter:
        Callable taking DeferredEvents and returning a string.
    """
    _FORMATTERS[name.lower()] = formatter


def get_formatter(name: str) -> Optional[Formatter]:
    """
    Retrieve a previously registered formatter.

    Parameters
    ----------
    name:
        Logical key used during registration.

    Returns
    -------
    Formatter | None
        The formatter callable if found, otherwise None.
    """
    return _FORMATTERS.get(name.lower())


# --------------------------------------------------------------------
# Built-in "pretty" formatter
# --------------------------------------------------------------------


def pretty_formatter(events: DeferredEvents) -> str:
    """
    Human-friendly multiline formatter for events.

    Format (stable and test-friendly):

        === EVENTS ===
        [LABEL] domain:stage via func_name
            kind: 'kind'
            message: ...
            exception: ...

    Notes
    -----
    - This mirrors the original textual layout that was previously
      implemented inline in Panopticon.
    - It is intended for CLI diagnostics and logs that should be
      readable by humans.
    """
    lines: list[str] = ["=== EVENTS ==="]

    for principle, evt in events:
        post = evt.post

        lines.append(
            f"[{principle.label.upper()}] {evt.domain}:{evt.stage} via {evt.func_name}"
        )

        if post is not None:
            lines.append(f"    kind: {post.kind!r}")
            if post.message:
                lines.append(f"    message: {post.message}")
            if post.exception is not None:
                lines.append(f"    exception: {post.exception!r}")

        lines.append("")

    return "\n".join(lines)


# Register default formatter
register_formatter("pretty", pretty_formatter)


__all__ = [
    "DeferredEvents",
    "Formatter",
    "register_formatter",
    "get_formatter",
    "pretty_formatter",
]
