# ================================================================
# architech/control/capture/context.py
# ================================================================
"""
ObservationContext — context-local LogBook manager.

This provides a single logical LogBook per execution context, so any
Capture usage writes to the same append-only log without manually
threading LogBook objects through function signatures.

It uses contextvars, so it works correctly with:
    - nested contexts
    - async/await
    - concurrent tasks
"""

from __future__ import annotations

import contextvars
import contextlib
from typing import Iterator

from .models import LogBook


class ObservationContext:
    """
    Context-local LogBook manager.

    Typical usage:

        from architech.control.capture import ObservationContext, Capture

        cap = Capture()

        with ObservationContext.push() as logbook:
            cap(my_fn, 42)
            ...
            events = list(logbook)
    """

    _CTX: contextvars.ContextVar[LogBook | None] = contextvars.ContextVar(
        "architech_control_capture_logbook",
        default=None,
    )

    @staticmethod
    def current() -> LogBook:
        """
        Return the current LogBook, creating one if none exists.

        This guarantees that Capture always has a LogBook to append to.
        """
        lb = ObservationContext._CTX.get()
        if lb is None:
            lb = LogBook()
            ObservationContext._CTX.set(lb)
        return lb

    @staticmethod
    @contextlib.contextmanager
    def push(logbook: LogBook | None = None) -> Iterator[LogBook]:
        """
        Install a new LogBook for the duration of the context.

        If `logbook` is None, a fresh LogBook is allocated.
        """
        token = ObservationContext._CTX.set(logbook or LogBook())
        try:
            yield ObservationContext._CTX.get()
        finally:
            ObservationContext._CTX.reset(token)
