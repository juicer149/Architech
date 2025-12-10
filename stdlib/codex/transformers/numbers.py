# ================================================================
# stdlib/codex/transformers/numbers.py
# ================================================================
"""
Numeric transformers for Codex stdlib.

These are pure transformations. They normally *do not* wrap
errors as Exceptions; unexpected failures raise and are treated
as hard errors by Codex.
"""

from __future__ import annotations

from typing import Any


def to_int(v: Any) -> Any:
    """
    Convert a value to int.

    Success:
        - return None if already int (no change)
        - or return converted int

    Failure:
        - return ValueError if conversion fails
    """
    if isinstance(v, int) and not isinstance(v, bool):
        return None

    try:
        value = int(v)
    except Exception:
        return ValueError(f"Cannot convert to int: {v!r}")

    return value
