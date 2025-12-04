# ================================================================
# architech/control/capture/__init__.py
# ================================================================
"""
capture — purely mechanical call-capture layer (zero semantics).

This package defines the mechanical stage of the event system:
it records what happened during a function call without assigning meaning.

Public API
----------
- CaptureConfig:
    Config object controlling how capture behaves.

- ValueSnapshot, PreInfo, PostInfo, Event:
    Mechanical data structures describing call behavior.

- LogBook:
    Append-only registry of mechanical events.

- ObservationContext:
    Context-local LogBook manager.

- Capture:
    Mechanical orchestrator:
        pre_capture → fn(...) → post_capture → Event
"""

from __future__ import annotations

from .config import CaptureConfig
from .models import ValueSnapshot, PreInfo, PostInfo, Event, LogBook
from .context import ObservationContext
from .pre import pre_capture, EMPTY_PRE
from .post import (
    build_post_from_result,
    build_post_from_exception,
    build_event,
)
from .capture import Capture

__all__ = [
    "CaptureConfig",
    "ValueSnapshot",
    "PreInfo",
    "PostInfo",
    "Event",
    "LogBook",
    "ObservationContext",
    "pre_capture",
    "EMPTY_PRE",
    "build_post_from_result",
    "build_post_from_exception",
    "build_event",
    "Capture",
]
