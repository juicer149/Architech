# ================================================================
# Architech/stdlib/codex/validators/numbers.py
# ================================================================
"""
Numeric validators for Codex stdlib.

All functions follow the “return Exception on failure” convention.
"""

from __future__ import annotations


def is_int(v):
    """
    Attempt to interpret v as int.

    Returns:
        - int(v) on success
        - ValueError(...) on failure
    """
    try:
        return int(v)
    except Exception:
        return ValueError(f"expected integer, got {v!r}")


def positive(v):
    """
    Require that v is >= 0.

    Assumes v is already numeric (e.g., via is_int).
    """
    try:
        if v < 0:
            return ValueError("must be positive")
    except Exception:
        return ValueError(f"expected comparable numeric, got {v!r}")
    return v


def in_range(min_val=None, max_val=None):
    """
    Build a range validator.

    Example:
        between_0_10 = in_range(0, 10)
        age_validator = in_range(0, 150)
    """

    def _check(v):
        try:
            if min_val is not None and v < min_val:
                return ValueError(f"value {v!r} < min {min_val!r}")
            if max_val is not None and v > max_val:
                return ValueError(f"value {v!r} > max {max_val!r}")
        except Exception:
            return ValueError(f"expected comparable numeric, got {v!r}")
        return v

    return _check
