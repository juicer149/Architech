# ================================================================
# architech/control/capture/config.py
# ================================================================
"""
CaptureConfig — options controlling the mechanical capture layer.

This configuration specifies *how* Capture should behave, without
introducing any semantics. It contains only mechanical options:

    domain            – logical domain string ("User.email")
    stage             – pipeline stage identifier ("1", "1.2", ...)
    capture_values    – whether to store snapshots of values
    capture_types     – whether to store type information
    measure_micro_time – whether to measure execution time

Upper layers (Panopticon, Judge) may combine this with a Principle,
which provides semantic meaning via labels and rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, Type, Any
@dataclass(frozen=True, slots=True)
class CaptureValue:
    """
    Policy for capturing a value and/or enforcing accepted types.

    capture:
        If True, Capture will record value/type snapshots depending on
        CaptureConfig flags (capture_values/capture_types). If False,
        values pass through unless an exception or type mismatch occurs.

    types:
        Optional tuple of accepted types. If provided, a mismatch will
        trigger Event creation regardless of capture flags. When combined
        with capture flags, snapshots may include the offending type/value.
    """

    capture: bool = False
    types: Optional[Tuple[Type[Any], ...]] = None


@dataclass(frozen=True, slots=True)
class CaptureConfig:
    """
    Mechanical configuration for Capture.

    All fields are optional to allow lightweight configurations.
    """

    domain: Optional[str] = None
    stage: str = "run"

    measure_micro_time: Optional[bool] = None

    # Input/output policies using CaptureValue.
    # None → fast path (no value capture; only exceptions create events).
    input: Optional[CaptureValue] = None
    output: Optional[CaptureValue] = None
