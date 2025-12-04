# ================================================================
# architech/control/effect/effect.py
# ================================================================
"""
EffectExe facade — glue between formatters and effect executors.

Panopticon calls this module as the last step in handling semantic
events:

    EffectExe.realize(
        effect="print",
        events=[(principle, event), ...],
        style="pretty",
    )

Responsibilities
----------------
- Select a formatter:
    • an explicit `formatter` callable, or
    • a named style via the formatter registry (e.g. "pretty").

- Render events into text.

- Select an executor via the effect executor registry (e.g. "print", "raise").

- Invoke the executor with the rendered text.

Custom exceptions
-----------------
For RAISE-like effects (effect key "raise"), EffectExe inspects the
involved Principles and, if any of them define `exc_type`, that type is
used as the final exception type. Otherwise RuntimeError is used.

This allows domain code to define:

    Principle("missing_@", praxis, Effect.RAISE, exc_type=MyCustomError)

and have both Codex strict-mode and the control effect layer raise
`MyCustomError` instead of a generic RuntimeError.
"""

from __future__ import annotations

from typing import Any, Optional, List, Tuple

from control.config import Principle
from control.effect.formatter import (
    DeferredEvents,
    Formatter,
    get_formatter,
    pretty_formatter,
)
from control.effect.executor import get_executor


DEFAULT_STYLE = "pretty"


class EffectExe:
    """
    Static facade for realizing effects for events.

    Typical usage (from Panopticon):

        EffectExe.realize(
            effect="print",
            events=deferred,
            style="pretty",
        )

    or with a custom formatter:

        EffectExe.realize(
            effect="json",
            events=deferred,
            formatter=my_json_formatter,
        )

    Panopticon is responsible for deciding which `effect` to use and
    in which order effects should be realized. EffectExe is responsible
    for mapping those choices to concrete formatters and executors.
    """

    # ------------------------------------------------------------
    # Formatter resolution
    # ------------------------------------------------------------
    @staticmethod
    def _resolve_formatter(
        *,
        formatter: Optional[Formatter],
        style: Optional[str],
    ) -> Formatter:
        """
        Resolve the effective formatter according to precedence:

            1. Explicit formatter callable (if provided)
            2. Named style from registry (style or DEFAULT_STYLE)
            3. Built-in pretty_formatter as ultimate fallback

        This keeps Panopticon free from any formatting logic and allows
        higher-level code to override formatting strategy if necessary.
        """
        if formatter is not None:
            return formatter

        style_name = style or DEFAULT_STYLE
        reg = get_formatter(style_name)
        if reg is not None:
            return reg

        # Last-resort fallback: built-in pretty formatter
        return pretty_formatter

    # ------------------------------------------------------------
    # Exception type resolution for RAISE
    # ------------------------------------------------------------
    @staticmethod
    def _resolve_exc_type_for_raise(events: List[Tuple[Principle, Any]]) -> type[BaseException]:
        """
        Resolve the exception type to use when effect == "raise".

        Strategy:
            - Use the first Principle.exc_type that is not None.
            - If all are None, fall back to RuntimeError.
        """
        for principle, _ in events:
            exc_type = getattr(principle, "exc_type", None)
            if exc_type is not None:
                return exc_type
        return RuntimeError

    # ------------------------------------------------------------
    # Main entrypoint
    # ------------------------------------------------------------
    @staticmethod
    def realize(
        effect: str,
        events: DeferredEvents,
        *,
        style: Optional[str] = None,
        formatter: Optional[Formatter] = None,
        **kwargs: Any,
    ) -> None:
        """
        Realize an effect mode for a set of events.

        Parameters
        ----------
        effect:
            Logical key identifying how the text should be surfaced.
            Usually derived from Effect.key(), e.g.:
                Effect.PRINT → "print"
                Effect.RAISE → "raise"

        events:
            Iterable of (Principle, Event) pairs to be rendered.

        style:
            Optional formatter style name to use (e.g. "pretty").
            Ignored if `formatter` is provided.

        formatter:
            Optional explicit formatter callable.
            If given, `style` is ignored.

        kwargs:
            Reserved for future extensions (e.g. passing extra hints
            down to formatters or executors). Currently unused by the
            built-in implementations.

        Behavior
        --------
        - If no executor is registered for `effect`, this is a no-op.
        - If no formatter is found, the built-in pretty_formatter is used.
        - For RAISE effects, the final exception type may be taken from
          `Principle.exc_type` (RuntimeError as default).
        """
        # Materialize events into a list so we can iterate multiple times
        events_list: List[Tuple[Principle, Any]] = list(events)

        if not events_list:
            return

        # 1. Resolve formatter
        fmt = EffectExe._resolve_formatter(formatter=formatter, style=style)

        # 2. Render text
        text = fmt(events_list)

        # 3. Resolve executor
        exec_fn = get_executor(effect)
        if exec_fn is None:
            # No executor registered: silently ignore
            return

        # 4. Run executor (side-effect)
        if effect.lower() == "raise":
            exc_type = EffectExe._resolve_exc_type_for_raise(events_list)
            # Backwards compatibility: executor may or may not accept exc_type
            try:
                exec_fn(text, exc_type=exc_type)  # type: ignore[misc]
            except TypeError:
                # Fallback: call without exc_type
                exec_fn(text)  # type: ignore[misc]
        else:
            exec_fn(text)  # type: ignore[misc]


__all__ = [
    "EffectExe",
]
