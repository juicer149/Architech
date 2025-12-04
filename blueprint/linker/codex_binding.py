# ================================================================
# blueprint/linker/codex_binding.py
# ================================================================
"""
Binding models for Codex pipelines.

This layer binds:
    DSL → IR → Bound IR (with Section IDs + Principles + domain)

PipelineCompiler consumes CodexBinding.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple

from control.config import Principle
from blueprint.codex.models import (
    Section,
    Phase,
    CodexIR,
    CodexConfig,
    PhaseConfig,
)


@dataclass(frozen=True, slots=True)
class SectionBinding:
    section: Section
    id: str
    principle: Optional[Principle] = None


@dataclass(frozen=True, slots=True)
class PhaseBinding:
    phase: Phase
    sections: Tuple[SectionBinding, ...]
    config: PhaseConfig = PhaseConfig()

    def __iter__(self):
        return iter(self.sections)


@dataclass(frozen=True, slots=True)
class CodexBinding:
    codex: CodexIR
    phases: Tuple[PhaseBinding, ...]
    config: CodexConfig
    domain: str

    def __iter__(self):
        return iter(self.phases)
