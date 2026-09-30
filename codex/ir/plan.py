# =============================================================================
# architech/codex/ir/plan.py
# =============================================================================
"""
(6) PhasePlan — per-phase compiled result.

A PhasePlan is produced by the compiler and represents everything
needed to execute a single Phase.

Contains
--------
- phase:
    Phase enum (SET / GET / DELETE)
- pipeline:
    Compiled pipeline of Nodes
- write:
    Optional Output for normal values
- exc:
    Optional Output for exception channel

Notes
-----
- PhasePlan is IR-only and side-effect free.
- Routing behavior is implemented in runtime/routing.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .phase import Phase
from .pipeline import Pipeline
from .output import Output


@dataclass(slots=True)
class PhasePlan:
    phase: Phase
    pipeline: Pipeline
    write: Optional[Output] = None
    exc: Optional[Output] = None
