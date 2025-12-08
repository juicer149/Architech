# ================================================================
# Architech/stdlib/codex/transformers/__init__.py
# ================================================================
"""
Stdlib transformers for Codex.

Transformers:
    - modify the value
    - *raise* normally on unexpected problems (hard failure)

Validation logic should live in `validators/`.
"""

from .numbers import to_int
from .text import strip, normalize
from .email import normalize_email

__all__ = [
    "to_int",
    "strip",
    "normalize",
    "normalize_email",
]
