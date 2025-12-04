# ================================================================
# blueprint/linker/__init__.py
# ================================================================
"""
Linker layer — binds Codex IR to execution metadata.

Exports the Binding objects consumed by Codex pipelines.
"""

from .codex_binding import SectionBinding, PhaseBinding, CodexBinding

__all__ = ["SectionBinding", "PhaseBinding", "CodexBinding"]
