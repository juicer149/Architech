# ================================================================
# stdlib/codex/transformers/__init__.py
# ================================================================
"""
Stdlib transformers for Codex.

Transformers:

    - change the value
    - may return None (no change) or a new value
    - should return Exception on soft failure
      (rare; usually validation is in validators/*)

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
