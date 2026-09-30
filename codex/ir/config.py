# =============================================================================
# architech/codex/ir/config.py
# =============================================================================
"""
(7) PhaseConfig — runtime policy per Phase.

Responsibility
--------------
PhaseConfig binds *which* Outputs are active for a given Phase and
provides optional pre/post hooks.

This module is IR-only:
- declarative
- side-effect free
- no routing logic
- no writing, raising, logging

PhaseConfig does NOT decide:
- how values are written
- how exceptions are raised
- when effects are materialized

Those responsibilities belong to runtime/routing.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from .phase import Phase
from .output import Output


@dataclass(slots=True)
class PhaseConfig:
    """
    Runtime configuration for a single Phase.

    Fields
    ------
    phase:
        The Phase this config applies to.

    write:
        Output describing how *values* are handled.

    exc:
        Output describing how *exceptions* are handled.

    pre:
        Optional hook executed BEFORE pipeline execution.
        Signature: pre(value, instance, field_name, phase) -> value

    post:
        Optional hook executed AFTER routing.
        Signature: post(result, instance, field_name, phase) -> result
    """
    phase: Phase
    write: Output
    exc: Output
    pre: Optional[Callable[[Any, Any, str, Phase], Any]] = None
    post: Optional[Callable[[Any, Any, str, Phase], Any]] = None

    @property
    def write_is_enabled(self) -> bool:
        return bool(self.write.enabled)

    @property
    def exception_is_enabled(self) -> bool:
        return bool(self.exc.enabled)


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

def default_phase_config(phase: Phase) -> PhaseConfig:
    """
    Default PhaseConfig.

    Design
    ------
    - No destination logic here.
    - No phase-specific branching of behavior.
    - INHERENT behavior is interpreted by runtime.

    Defaults mean:
    - values: handled via Output(effect=INHERENT)
    - exceptions: handled via Output(effect=INHERENT)
    """
    return PhaseConfig(
        phase=phase,
        write=Output(is_exception=False, enabled=True),
        exc=Output(is_exception=True, enabled=True),
    )
