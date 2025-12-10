# ================================================================
# stdlib/codex/validators/text.py
# ================================================================
"""
Text validators for Codex stdlib.
"""

from __future__ import annotations

from typing import Any


def non_empty(v: Any) -> Any:
    """
    Require that `v` is a non-empty string after strip().

    Success:
        - return None (no change) if already non-empty after strip
        - or return stripped string if we removed whitespace

    Failure:
        - return ValueError(...)
    """
    if not isinstance(v, str):
        return ValueError(f"Expected string, got {type(v).__name__}")

    s = v.strip()
    if not s:
        return ValueError("value must not be empty")

    if s == v:
        return None
    return s
