# ================================================================
# Architech/stdlib/codex/validators/__init__.py
# ================================================================
"""
Stdlib validators for Codex.

Convention:
    - Validator functions return either:
        • a new value (success)
        • the same value (success)
        • an Exception instance (semantic failure)
    - They normally do *not* raise, because Codex interprets
      “return Exception” as semantic violation.

More specialized validators live in:
    - numbers.py
    - text.py
    - email.py
"""

from .numbers import is_int, positive, in_range
from .text import non_empty
from .email import require_at

__all__ = [
    "is_int",
    "positive",
    "in_range",
    "non_empty",
    "require_at",
]
