# ================================================================
# Architech/stdlib/codex/validators/text.py
# ================================================================
"""
Text validators for Codex stdlib.
"""

from __future__ import annotations


def non_empty(v):
    """
    Require that v is not an empty string after strip().

    Returns:
        - v (unchanged) on success
        - ValueError(...) on failure
    """
    s = str(v)
    if not s.strip():
        return ValueError("value must not be empty")
    return v
