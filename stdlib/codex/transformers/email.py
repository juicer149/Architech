# ================================================================
# Architech/stdlib/codex/transformers/email.py
# ================================================================
"""
Email transformers for Codex stdlib.
"""

from __future__ import annotations


def normalize_email(v):
    """
    Normalize email by applying strip + lower.

    (More advanced normalization may be added later.)
    """
    return str(v).strip().lower()
