# ============================================================================
# architech/codex/ir/__init__.py
# ============================================================================
"""
Codex IR (Intermediate Representation).

Defines passive, side-effect-free data structures used by the compiler
and runtime.

IR responsibilities
-------------------
- phases
- semantic metadata
- routing policy (declarative only)
- compiled nodes, pipelines, and plans

IR must NOT:
- write to instances
- raise runtime exceptions
- perform logging or warnings

Runtime behavior lives in codex/runtime/.
"""

from __future__ import annotations

from .phase import Phase
from .effect import Effect
from .timing import Timing
from .output import Output, TypeFilter, normalize_type_filter
from .node import Node, StepFn
from .pipeline import Pipeline
from .plan import PhasePlan
from .config import PhaseConfig, default_phase_config
from .contract import CodexIRContract, CODEX_CONTRACT

__all__ = [
    "Phase",

    # routing policy
    "Output",
    "Effect",
    "Timing",
    "TypeFilter",
    "normalize_type_filter",

    # structure
    "Node",
    "StepFn",
    "Pipeline",
    "PhasePlan",

    # runtime config
    "PhaseConfig",
    "default_phase_config",

    # contract
    "CodexIRContract",
    "CODEX_CONTRACT",
]
