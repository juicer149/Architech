# ================================================================
# stdlib/codex/validators/email.py
# ================================================================
"""
Email-related validators for Codex stdlib.
"""

from __future__ import annotations

from typing import Any


def require_at(v: Any) -> Any:
    """
    Require that the value contains '@'.

    Success:
        - return None  (no change)

    Failure:
        - return ValueError(...)
    """
    s = str(v)
    if "@" not in s:
        return ValueError("missing '@' in email")
    return None


def is_email(v: Any) -> Any:
    """
    Lightweight email validation.

    Success:
        - return None (no change)

    Failure:
        - return ValueError

    NOTE:
        This is intentionally minimal and not RFC-complete.
    """
    s = str(v).strip()
    if "@" not in s or s.count("@") != 1:
        return ValueError("invalid email: missing single '@'")
    local, domain = s.split("@", 1)
    if not local or not domain or "." not in domain:
        return ValueError("invalid email: malformed local or domain part")
    return None
