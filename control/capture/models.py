# ================================================================
# architech/control/capture/models.py
# ================================================================
"""
Mechanical data models for the capture layer.

Purpose
-------
These are **purely mechanical objects** describing what occurred during
a function call — without semantics, categorization, or control-flow
decisions.

Models
------
ValueSnapshot:
    Optional (value, type) capture. JSON-friendly.

PreInfo:
    Pre-call mechanical snapshot:
        - received: optional ValueSnapshot for the input value
        - t0: optional floating timestamp (perf_counter) for timing

PostInfo:
    Post-call mechanical outcome:
        - kind: "value", "returned_exception", "exception_raised", ...
        - returned: ValueSnapshot for the output (if captured)
        - exception: raised/returned exception
        - exception_is_raise: True if the exception came from a Python
          `raise`, False if it was returned as a value
        - message: human-readable info

Event:
    Timestamped contextual wrapper:
        - ts       : timestamp (UTC) or None
        - domain   : logical domain (e.g. "User.email") or None
        - stage    : pipeline stage (e.g. "1", "1.2") or None
        - func_name: name of the underlying function or None
        - label    : semantic tag injected by upper layers or None
        - duration : optional duration in seconds
        - pre      : optional PreInfo
        - post     : optional PostInfo

LogBook:
    Append-only collection of Events.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Optional, List, Dict, Iterator
import time


# ------------------------------------------------------------
# ValueSnapshot
# ------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ValueSnapshot:
    """
    Optional capture of a Python value and its type.

    Both fields are optional so callers can choose to store only the type
    or only the value, depending on privacy/performance requirements.
    """
    value: Optional[Any] = None
    type: Optional[type] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "type": self.type.__name__ if self.type else None,
        }


# ------------------------------------------------------------
# PreInfo — pre-call mechanical snapshot
# ------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class PreInfo:
    """
    Pre-call mechanical snapshot.

    received:
        Optional ValueSnapshot of the input value. Typically the first
        positional argument to the observed function.

    t0:
        Optional high-resolution timestamp from time.perf_counter(),
        used for computing durations.
    """
    received: Optional[ValueSnapshot] = None
    t0: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["received"] = (
            self.received.to_dict() if self.received is not None else None
        )
        return data


# ------------------------------------------------------------
# PostInfo — post-call mechanical outcome
# ------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class PostInfo:
    """
    Post-call mechanical outcome description.

    kind:
        String describing the outcome type:
            - "value"
            - "returned_exception"
            - "exception_raised"
            - other future variants

    returned:
        Optional ValueSnapshot describing the returned value (if captured).

    exception:
        Raised or returned exception instance, if any.

    exception_is_raise:
        True if the exception was produced via a Python `raise`.
        False if the exception was produced via a normal `return`
        (soft error pattern in Codex pipelines).

    message:
        Human-readable description, usually str(exception) when present.

    Important:
        This structure is **purely mechanical**. It does not decide whether
        an exception should abort, be deferred, or be ignored — that is the
        job of the Judge/Executor layer.
    """
    kind: Optional[str] = None

    returned: Optional[ValueSnapshot] = None

    exception: Optional[BaseException] = None
    exception_is_raise: bool = False
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["returned"] = (
            self.returned.to_dict() if self.returned is not None else None
        )
        data["exception"] = (
            repr(self.exception) if self.exception is not None else None
        )
        return data


# ------------------------------------------------------------
# Event — contextualized pre + post
# ------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Event:
    """
    Mechanical event wrapper combining context + PreInfo + PostInfo.

    All attributes are optional to allow very small objects when running
    in minimal-capture modes; the builders in `post.py` specialize common
    patterns and fill in what is available.
    """
    ts: Optional[str] = None
    domain: Optional[str] = None
    stage: Optional[str] = None
    func_name: Optional[str] = None

    # Already Optional
    label: Optional[str] = None
    duration: Optional[float] = None

    pre: Optional[PreInfo] = None
    post: Optional[PostInfo] = None

    @classmethod
    def from_parts(
        cls,
        *,
        domain: Optional[str],
        stage: Optional[str],
        func_name: Optional[str],
        label: Optional[str],
        duration: Optional[float],
        pre: Optional[PreInfo],
        post: Optional[PostInfo],
    ) -> "Event":
        """
        Build an Event from the given context and mechanical parts.

        Timestamp:
            Use time.time_ns() — fastest monotonic-ish wall-clock source.
        """
        ts = str(time.time_ns())  # <---- FASTEST TIMESTAMP

        return cls(
            ts=ts,
            domain=domain,
            stage=stage,
            func_name=func_name,
            label=label,
            duration=duration,
            pre=pre,
            post=post,
        )

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.pre is not None:
            data["pre"] = self.pre.to_dict()
        if self.post is not None:
            data["post"] = self.post.to_dict()
        return data


# ------------------------------------------------------------
# LogBook
# ------------------------------------------------------------

@dataclass(slots=True)
class LogBook:
    """
    Append-only container of Event instances.

    The capture layer does not impose any indexing or querying strategy;
    higher layers are free to interpret events as they wish.
    """
    _events: List[Event] = field(default_factory=list)

    def append(self, event: Event) -> None:
        self._events.append(event)

    def __iter__(self) -> Iterator[Event]:
        return iter(self._events)

    def __len__(self) -> int:
        return len(self._events)

    def last(self) -> Optional[Event]:
        """O(1) fast-path retrieval of newest event."""
        return self._events[-1] if self._events else None

    def to_events(self) -> List[Event]:
        """Return raw Event objects."""
        return list(self._events)

    def to_list(self) -> List[Dict[str, Any]]:
        return [evt.to_dict() for evt in self._events]
