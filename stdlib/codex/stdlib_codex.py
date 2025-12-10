# ================================================================
# stdlib/codex/stdlib_codex.py
# ================================================================
"""
StdCodex — thin wrapper around the core `codex.Codex`.

Purpose is purely semantic:
    - `codex.Codex` is the generic descriptor.
    - `StdCodex` is the "stdlib variant" used inside stdlib/codex and
      recommended for user code that relies on stdlib semantics.

This gives a semantic marker ("this is a stdlib pipeline") and provides
a convenient hook if you ever want stdlib-specific defaults.
"""

from __future__ import annotations

from typing import Any, Optional

from codex import Codex as _CoreCodex


class StdCodex(_CoreCodex):
    """
    Stdlib variant of Codex.

    Currently behaves identically to `codex.Codex`, but acts as a clear
    semantic boundary between core and stdlib and is a natural place for
    stdlib-specific defaults in the future.
    """

    def __init__(
        self,
        *sections: Any,
        strict: Optional[bool] = None,
        default: Any = None,
    ):
        super().__init__(*sections, strict=strict, default=default)
