# ================================================================
# Architech/stdlib/codex/stdlib_codex.py
# ================================================================
"""
StdCodex — thin wrapper around core `codex.Codex`.

Purpose is purely semantic:
    - `codex.Codex` is the general descriptor.
    - `StdCodex` is the “stdlib variant” used within stdlib/codex
      and exportable for building pipelines based on
      SET/GET + stdlib principles.
"""

from __future__ import annotations

from typing import Any, Optional

from codex import Codex as _CoreCodex


class StdCodex(_CoreCodex):
    """
    Stdlib variant of Codex.

    Behaves identically to `codex.Codex`, but serves as a semantic
    marker (“this is a stdlib pipeline”) and provides a future hook
    should stdlib-specific defaults ever be needed.
    """

    def __init__(self, *sections: Any, strict: Optional[bool] = None, default: Any = None):
        super().__init__(*sections, strict=strict, default=default)
