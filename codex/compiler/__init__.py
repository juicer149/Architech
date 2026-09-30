# =============================================================================
# architech/codex/compiler/__init__.py
# =============================================================================
"""
Compiler layer: DSL Section -> Codex IR.

The compiler consumes backend-agnostic dsl.Section objects and produces:
- PhasePlan per Phase
- Pipeline (list of Node)

Runtime behavior is not implemented here.
"""

from __future__ import annotations

from .compile import compile_sections

__all__ = ["compile_sections"]
