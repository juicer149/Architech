# ================================================================
# architech/control/capture/capture.py
# ================================================================
"""
Capture — mechanical call-capture orchestrator.

Lifecycle:
    pre_capture → fn(...) → post_capture → Event

Capture is **pure mechanics**:
    • no semantics
    • no principles
    • no praxis
    • no judgement

Upper layers may inject a semantic `label` AFTER the Event is created.

Capture NEVER decides control flow:
    - it does NOT re-raise exceptions
    - it does NOT abort or defer
    - it only records what happened
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, TypeVar, cast

from .config import CaptureConfig, CaptureValue
from .context import ObservationContext
from .pre import pre_capture, EMPTY_PRE
from .post import (
    build_post_from_result,
    build_post_from_exception,
    build_event,
)
from .models import PreInfo, PostInfo

F = TypeVar("F", bound=Callable[..., Any])


@dataclass(slots=True)
class Capture:
    """
    Mechanical call-capture orchestrator.

    Attributes
    ----------
    default_domain:
        Fallback domain used when the CaptureConfig omits a domain.

    capture_values_default / capture_types_default:
        Defaults used by the decorator API when CaptureConfig is not passed.
    """

    default_domain: str = "default"
    capture_values_default: bool = False
    capture_types_default: bool = False

    # ------------------------------------------------------------
    # Decorator API
    # ------------------------------------------------------------
    def decorator(
        self,
        *,
        config: Optional[CaptureConfig] = None,
    ) -> Callable[[F], F]:
        """
        Decorator form of Capture.

        Example:

            cap = Capture(domain="User.email")

            @cap.decorator(config=CaptureConfig(stage="1"))
            def validate_email(value: str):
                ...
        """

        def decorate(fn: F) -> F:
            cfg = config or CaptureConfig(
                domain=self.default_domain,
                capture_values=self.capture_values_default,
                capture_types=self.capture_types_default,
            )

            def wrapper(*args, **kwargs):
                return self(fn, *args, config=cfg, **kwargs)

            return cast(F, wrapper)

        return decorate

    # ------------------------------------------------------------
    # Main call logic
    # ------------------------------------------------------------
    def __call__(
        self,
        fn: Callable[..., Any],
        *args,
        config: Optional[CaptureConfig] = None,
        label: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Execute `fn` and, depending on config, capture a mechanical Event.

        FAST PATH:
            If config captures nothing (values, types, time = off),
            then Capture performs zero allocations and returns raw result.

        SLOW PATH:
            pre_capture → fn → post_capture → build_event → append LogBook
        """

        # If no config is provided, use default domain/stage and no capture.
        cfg = config or CaptureConfig(domain=self.default_domain)

        # Resolve concrete behavior
        domain = cfg.domain or self.default_domain
        stage = cfg.stage
        use_timer = bool(cfg.measure_micro_time)
        in_policy: Optional[CaptureValue] = cfg.input
        out_policy: Optional[CaptureValue] = cfg.output

        # Compute capture flags from policies
        capture_values = bool((in_policy and in_policy.capture) or (out_policy and out_policy.capture))
        capture_types = capture_values  # simplified: when capturing, include type snapshots if desired

        fast_path = not (use_timer or capture_values or capture_types)

        # PRE (only allocate if capturing or timing)
        pre: PreInfo
        if fast_path:
            pre = EMPTY_PRE
        else:
            pre = pre_capture(
                args,
                capture_value=capture_values,
                capture_type=capture_types,
                measure_micro_time=use_timer,
            )

        # Type gate on input (no allocations)
        input_type_violation = False
        if in_policy is not None and in_policy.types is not None:
            try:
                input_type_violation = any(
                    (arg is not None) and (not isinstance(arg, in_policy.types))
                    for arg in args
                )
            except TypeError:
                input_type_violation = False

        # EXEC
        try:
            result = fn(*args, **kwargs)
            post: Optional[PostInfo] = build_post_from_result(
                result,
                pre=pre,
                capture_value=capture_values,
                capture_type=capture_types,
            )
        except BaseException as exc:
            result = None
            post = build_post_from_exception(exc, pre=pre)

        # Output type gate
        output_type_violation = False
        if post is None and out_policy is not None and out_policy.types is not None and result is not None:
            try:
                output_type_violation = not isinstance(result, out_policy.types)
            except TypeError:
                output_type_violation = False

        # Fast pass-through if no post and no violations
        if post is None and not input_type_violation and not output_type_violation:
            return result

        # EVENT
        func_name = getattr(fn, "__name__", repr(fn))
        evt = build_event(
            domain=domain,
            stage=stage,
            func_name=func_name,
            label=label,
            pre=pre if not fast_path else None,
            post=post,
        )
        ObservationContext.current().append(evt)

        return result
