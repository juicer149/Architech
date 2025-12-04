# ================================================================
# architech/control/effect/executor.py
# ================================================================
"""
Effect executor registry — how rendered text is surfaced.

This module is responsible for taking *rendered text* and performing
a side-effect, for example:

    - printing to stdout
    - raising an aggregated exception
    - sending an email (future)
    - writing to a file (future)
    - emitting a log record (future)

Concepts
--------
- Executor:
    Callable that takes a string (and possibly extra keyword arguments)
    and performs a side-effect.

Registry
--------
- register_executor(mode, executor):
    Register an executor for a logical effect mode.

- get_executor(mode) -> Executor | None:
    Lookup an executor by mode name (case-insensitive).

Built-ins
---------
- eff_print:
    Print rendered text to stdout.

- eff_raise:
    Raise RuntimeError (or a custom exception type) with text as message.

The `exc_type` for eff_raise is typically provided by higher-level code,
such as EffectExe when realizing Effect.RAISE. If none is provided,
RuntimeError is used.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional, Type


# --------------------------------------------------------------------
# Types
# --------------------------------------------------------------------

Executor = Callable[..., None]


# --------------------------------------------------------------------
# Registry
# --------------------------------------------------------------------

_EXECUTORS: Dict[str, Executor] = {}


def register_executor(mode: str, executor: Executor) -> None:
    """
    Register an executor for a logical effect mode.

    Parameters
    ----------
    mode:
        Logical key for effect behavior (e.g. "print", "raise", "json").
        Lowercased before insertion.

    executor:
        Callable taking a rendered text string and performing
        a side-effect. It is recommended that executors accept
        **kwargs to support future extensions (e.g. custom exception
        types for "raise").
    """
    _EXECUTORS[mode.lower()] = executor


def get_executor(mode: str) -> Optional[Executor]:
    """
    Retrieve an executor for the given effect mode.

    Parameters
    ----------
    mode:
        Logical key used during registration.

    Returns
    -------
    Executor | None
        The executor callable if found, otherwise None.
    """
    return _EXECUTORS.get(mode.lower())


# --------------------------------------------------------------------
# Built-in executors
# --------------------------------------------------------------------


def eff_print(text: str, **kwargs) -> None:
    """
    Default executor for mode="print".

    Simply prints the text block to stdout.
    Additional keyword arguments are ignored.
    """
    print(text)


def eff_raise(
    text: str,
    *,
    exc_type: Type[BaseException] = RuntimeError,
    **kwargs,
) -> None:
    """
    Default executor for mode="raise".

    Parameters
    ----------
    text:
        Rendered text describing events.

    exc_type:
        Exception type to raise. Defaults to RuntimeError.

    kwargs:
        Reserved for future extensions; currently ignored.

    Behavior
    --------
    Raises `exc_type(text)`.
    """
    raise exc_type(text)


# Register default modes
register_executor("print", eff_print)
register_executor("raise", eff_raise)


__all__ = [
    "Executor",
    "register_executor",
    "get_executor",
    "eff_print",
    "eff_raise",
]
