# ================================================================
# architech/control/capture/post.py
# ================================================================
"""
post.py — post-call mechanical normalization and Event construction.

This module interprets the mechanical outcomes of a call:

    - normal return
    - returned PostInfo
    - returned exception
    - raised exception

It produces a PostInfo and, if desired, wraps PreInfo + PostInfo into
an Event via `build_event`.

Important:
    This layer does NOT perform any semantic decisions (abort/defer/etc).
    It only describes what mechanically happened.
"""

from __future__ import annotations

from time import perf_counter
from typing import Any, Optional

from .models import ValueSnapshot, PreInfo, PostInfo, Event


# ------------------------------------------------------------
# PostInfo builders
# ------------------------------------------------------------

def build_post_from_result(
    result: Any,
    *,
    pre: PreInfo,
    capture_value: bool,
    capture_type: bool,
) -> Optional[PostInfo]:
    """
    Normalize the result of a successful call into a PostInfo.

    Cases:
        - result is PostInfo:
            returned as-is.

        - result is BaseException:
            treated as a *returned* exception (soft error pattern).
            exception_is_raise is False.

        - result is any other value:
            if capture_value/capture_type are False → return None (fast path).
            otherwise → build a "value" PostInfo with a ValueSnapshot.
    """
    if isinstance(result, PostInfo):
        return result

    if isinstance(result, BaseException):
        return PostInfo(
            kind="returned_exception",
            returned=None,
            exception=result,
            exception_is_raise=False,
            message=str(result),
        )

    if not (capture_value or capture_type):
        return None

    returned = ValueSnapshot(
        value=result if capture_value else None,
        type=type(result) if capture_type else None,
    )

    return PostInfo(
        kind="value",
        returned=returned,
        exception=None,
        exception_is_raise=False,
        message=None,
    )


def build_post_from_exception(exc: BaseException, *, pre: PreInfo) -> PostInfo:
    """
    Build a PostInfo describing a *raised* exception.

    This is used when the underlying function raises instead of returning.
    exception_is_raise is set to True so upper layers can distinguish this
    from a soft error (exception-return pattern).
    """
    return PostInfo(
        kind="exception_raised",
        returned=None,
        exception=exc,
        exception_is_raise=True,
        message=str(exc),
    )


# ------------------------------------------------------------
# Event builder
# ------------------------------------------------------------

def build_event(
    *,
    domain: Optional[str],
    stage: Optional[str],
    func_name: Optional[str],
    label: Optional[str],
    pre: Optional[PreInfo],
    post: Optional[PostInfo],
) -> Event:
    """
    Build an Event from the given context and mechanical parts.

    Duration is computed from pre.t0 if present; otherwise None.
    """
    if pre is not None and pre.t0 is not None:
        duration = perf_counter() - pre.t0
    else:
        duration = None

    return Event.from_parts(
        domain=domain,
        stage=stage,
        func_name=func_name,
        label=label,
        duration=duration,
        pre=pre,
        post=post,
    )
