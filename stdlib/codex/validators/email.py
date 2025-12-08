# ================================================================
# Architech/stdlib/codex/validators/email.py
# ================================================================
"""
Email-related validators for Codex stdlib.
"""

from __future__ import annotations


def require_at(v):
    """
    Require that the value contains '@'.

    Returns:
        - v on success
        - ValueError(...) on failure
    """
    s = str(v)
    if "@" not in s:
        return ValueError("missing @")
    return v

#should add a more robust email validator later
