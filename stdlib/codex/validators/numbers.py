# ================================================================
# stdlib/codex/validators/numbers.py
# ================================================================
"""
Numeric validators for Codex stdlib.

All functions follow the "return Exception on semantic failure"
convention expected by Codex:

    - On success:
        • return None  → no change
        • or return a (possibly modified) value

    - On soft failure (validation failure):
        • return an Exception instance

    - They should NOT raise directly except on bugs.
"""

from __future__ import annotations

from typing import Any, Callable


def is_int(x: Any) -> Any:
    """
    Check if the value is an int (without coercion).

    Success:
        - return None  if isinstance(x, int) and not bool

    Failure:
        - return ValueError otherwise
    """
    if isinstance(x, int) and not isinstance(x, bool):
        return None
    return ValueError(f"Expected int, got {type(x).__name__}: {x!r}")


def positive(x: Any) -> Any:
    """
    Ensure that a numeric value is strictly positive (> 0).

    Success:
        - return None

    Failure:
        - return ValueError
    """
    try:
        v = float(x)
    except Exception:
        return ValueError(f"Expected numeric value, got {x!r}")

    if v > 0:
        return None
    return ValueError(f"Expected positive number, got {x!r}")


def in_range(
    min_val: float | None = None,
    max_val: float | None = None,
) -> Callable[[Any], Any]:
    """
    Build a validator that checks numeric ranges.

    Example:
        between_0_and_10 = in_range(0, 10)
        age_validator = in_range(0, 150)

        (SET >> between_0_and_10) @ ERROR

    Constraints are inclusive: [min_val, max_val].

    Success:
        - return None

    Failure:
        - return ValueError
    """

    def _check(x: Any) -> Any:
        try:
            v = float(x)
        except Exception:
            return ValueError(f"Expected numeric value, got {x!r}")

        if min_val is not None and v < min_val:
            return ValueError(f"value {v!r} < min {min_val!r}")
        if max_val is not None and v > max_val:
            return ValueError(f"value {v!r} > max {max_val!r}")
        return None

    return _check
