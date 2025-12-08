# ================================================================
# Architech/stdlib/codex/transformers/numbers.py
# ================================================================
"""
Numeric transformers for Codex stdlib.

These are pure transformations and *raise* on hard errors.
"""

from __future__ import annotations


def to_int(v):
    """
    Pure int conversion.

    Raises on failure (treated as “bug/unexpected” at Codex level).
    """
    return int(v)
