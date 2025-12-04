# ================================================================
# architech/control/capture/pre.py
# ================================================================
"""
pre.py — pre-call mechanical capture helpers.

Responsible for:
    - optionally capturing a ValueSnapshot of the input
    - optionally starting a micro-timer
    - returning a PreInfo used by post-call builders and Capture
"""

from __future__ import annotations

from time import perf_counter
from typing import Any

from .models import ValueSnapshot, PreInfo


# A canonical "empty" pre-info instance for fast-path usage
EMPTY_PRE = PreInfo(received=None, t0=None)


def pre_capture(
    args: tuple[Any, ...],
    *,
    capture_value: bool,
    capture_type: bool,
    measure_micro_time: bool,
) -> PreInfo:
    """
    Build a PreInfo object from the given call arguments.

    Only the first positional argument is considered as "received"
    value for now — this matches typical "transform(value)" codex
    pipelines and keeps the capture logic minimal.
    """
    if args and (capture_value or capture_type):
        raw = args[0]
        received = ValueSnapshot(
            value=raw if capture_value else None,
            type=type(raw) if capture_type else None,
        )
    else:
        received = None

    t0 = perf_counter() if measure_micro_time else None
    return PreInfo(received=received, t0=t0)
