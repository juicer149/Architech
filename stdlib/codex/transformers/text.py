# ================================================================
# stdlib/codex/transformers/text.py
# ================================================================
"""
Text transformers for Codex stdlib.
"""

from __future__ import annotations

from typing import Any


def strip(v: Any) -> Any:
    """
    Strip leading/trailing whitespace from a string.

    Success:
        - return None if no change
        - or return stripped string

    Failure:
        - return ValueError on non-string input
    """
    if not isinstance(v, str):
        return ValueError(f"Expected string, got {type(v).__name__}")
    s = v.strip()
    if s == v:
        return None
    return s


def normalize(v: Any) -> Any:
    """
    Simple normalization: lowercase string.

    Success:
        - return None if already normalized
        - or return normalized string

    Failure:
        - return ValueError on non-string input
    """
    if not isinstance(v, str):
        return ValueError(f"Expected string, got {type(v).__name__}")
    lowered = v.lower()
    if lowered == v:
        return None
    return lowered
