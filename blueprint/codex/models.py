# ================================================================
# blueprint/codex/models.py
# ================================================================
"""
Domain AST and configuration models for Codex pipelines.

Codex consumes DSL StepChain objects and produces a domain-specific IR:

    CodexIR
        → PhaseNode (Phase + PhaseConfig)
            → Section
                → Step

Plus configuration objects:

    - CodexConfig    (global settings)
    - PhaseConfig    (per-phase overrides)

Semantics (Principle, Praxis, Effect) live in `control.config` and are
attached later via bindings. This module is pure AST + configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Optional, Tuple


# ---------------------------------------------------------------------------
# Primitive alias
# ---------------------------------------------------------------------------

Fn = Callable[[Any], Any]


# ============================================================
# AST NODES
# ============================================================


@dataclass(frozen=True, slots=True)
class Step:
    """
    Smallest atomic unit in a pipeline.

    Attributes
    ----------
    fn:
        Primary function to execute.

    fallbacks:
        Functions to try if the primary fn fails (raises), in the
        order provided.
    """

    fn: Fn
    fallbacks: Tuple[Fn, ...] = ()

    def __iter__(self):
        """Iterate over primary + fallbacks for introspection."""
        yield self.fn
        yield from self.fallbacks


@dataclass(frozen=True, slots=True)
class Section:
    """
    A Section groups one or more Steps.

    steps:
        Ordered tuple of Steps.

    A Section is iterable over its Steps so that pipeline compilation
    and execution becomes natural:

        for step in section:
            ...
    """

    steps: Tuple[Step, ...]


class Phase(Enum):
    """
    Execution phase for a Codex pipeline.

    SET:
        Runs on attribute assignment. Typical use:
            - validation
            - normalization
            - transformation

    GET:
        Runs on attribute access. Typical use:
            - masking
            - decoding/decrypting for presentation
            - view-time decorations
    """

    SET = auto()
    GET = auto()


# ============================================================
# CONFIGURATION OBJECTS
# ============================================================


@dataclass(frozen=True, slots=True)
class CodexConfig:
    """
    Global configuration for a Codex pipeline.

    strict:
        Controls overall execution mode:

            True  → strictly direct calls, no Panopticon/control layer
                     (but Principles may still map exceptions via
                      `exc_type` if present).

            False → interpreted-only (Panopticon required)
                     (Praxis + Effect are fully honored).

            None  → auto (decide based on presence of semantics)
    """

    strict: Optional[bool] = None
    # Future global flags can be added here.


@dataclass(frozen=True, slots=True)
class PhaseConfig:
    """
    Per-phase configuration override.

    strict:
        If not None, overrides CodexConfig.strict for this phase.

        Resolution (conceptual):

            if phase.strict is not None:
                use phase.strict
            elif codex.strict is not None:
                use codex.strict
            else:
                auto-mode based on semantics

    dest:
        Optional destination hint for the final value of this phase.
        Currently this is an advisory metadata field; Codex 3.x
        always stores the internal value on the owning instance.

        Future use could support:

            - routing values to a secondary attribute
            - emitting into an external model (e.g. SQLAlchemy)
            - composing multiple "views" of the same input.
    """

    strict: Optional[bool] = None
    dest: Any = None
    # Probe mode for interpreted fallbacks: "none" | "exceptions" | "full"
    # none: no capture/semantics during fallback probes
    # exceptions: record events only for exceptions/type mismatches
    # full: capture values/types for fallback probes (same as primary)
    probe_capture: str = "none"
    # Default value-capture preference for interpreted observation
    # If False, only exceptions/type gates produce events.
    capture_values: bool = True


# ============================================================
# AST CONTAINERS
# ============================================================


@dataclass(frozen=True, slots=True)
class PhaseNode:
    """
    Group Sections under a Phase and PhaseConfig.

    This is the natural iteration unit:

        for section in phase_node:
            ...

    The AST does NOT carry IDs or Principles — those are bound later.
    """

    phase: Phase
    sections: Tuple[Section, ...]
    config: PhaseConfig = PhaseConfig()

    def __iter__(self):
        return iter(self.sections)


@dataclass(frozen=True, slots=True)
class CodexIR:
    """
    Root of the Codex AST for a single attribute pipeline.

    phases:
        Ordered tuple of PhaseNode objects. For Codex 3.x we use
        at most two phases: SET and GET.

    config:
        Global Codex-level configuration (e.g. strict).
    """

    phases: Tuple[PhaseNode, ...]
    config: CodexConfig = CodexConfig()

    def __iter__(self):
        return iter(self.phases)
