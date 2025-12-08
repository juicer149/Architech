# ================================================================
# Architech/stdlib/codex/transformers/text.py
# ================================================================
"""
Text transformers for Codex stdlib.
"""

from __future__ import annotations


def strip(v):
    return str(v).strip()


def normalize(v):
    """
    Simple normalization: strip + lower.
    """
    return str(v).strip().lower()
