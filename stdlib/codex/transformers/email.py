# ================================================================
# stdlib/codex/transformers/email.py
# ================================================================
"""
Email transformers for Codex stdlib.
"""

from __future__ import annotations

from typing import Any


def normalize_email(v: Any) -> Any:
    """
    Normalize email by strip + lower.

    Success:
        - return normalized string

    Failure:
        - never fails here; use validators.email.is_email / require_at
          for validation.
    """
    return str(v).strip().lower()
