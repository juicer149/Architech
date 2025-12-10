# ================================================================
# stdlib/codex/validators/__init__.py
# ================================================================
"""
Stdlib validators for Codex.

Convention:
    - Validator functions return either:
        • None            (success, no change)
        • a new value     (success, modified)
        • an Exception    (semantic failure)

    - They normally do NOT raise; Codex treats "return Exception"
      as a signal for semantic violations in semantic mode.

More specialised validators live in:
    - numbers.py
    - text.py
    - email.py
"""

from .numbers import is_int, positive, in_range
from .text import non_empty
from .email import require_at, is_email

__all__ = [
    "is_int",
    "positive",
    "in_range",
    "non_empty",
    "require_at",
    "is_email",
]
