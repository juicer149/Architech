# ================================================================
# blueprint/codex/factory.py
# ================================================================
"""
Factory functions for constructing Codex IR + bindings from DSL.

Pipeline:

    StepChain / Fn  → Sections (+Principles, per Phase)
                     → CodexIR (SET/GET phases)
                     → Section IDs per Phase
                     → SectionBinding / PhaseBinding / CodexBinding

This keeps:
    - models.py pure (AST + configs)
    - bindings.py focused (metadata)
    - pipeline.py simple (compilation)
    - codex.py with a single entrypoint: build_codex_binding()

The DSL layer (blueprint.dsl) is entirely generic. Codex interprets
its phase keys and semantic tokens into concrete Phase, Principle, and
PhaseConfig objects.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from control.config import Principle

from ..dsl import StepChain
from ..dsl.nodes import SectionNode, StepNode
from .models import (
    Fn,
    Step,
    Section,
    Phase,
    PhaseNode,
    CodexIR,
    CodexConfig,
    PhaseConfig,
)
from blueprint.linker.codex_binding import (
    SectionBinding,
    PhaseBinding,
    CodexBinding,
)
from .constants import DEFAULT_PHASE
from control.semantics import to_principle


# ================================================================
# StepChain / Fn → Section
# ================================================================


def _build_section_from_node(node: SectionNode) -> Section:
    """
    Convert a SectionNode (AST) into a Section (IR) with one or more Steps.

    The SectionNode contains all necessary info; we only translate
    StepNode(primary, fn) into IR Step(Fn, fallbacks).
    """
    steps: List[Step] = []
    current_fn: Optional[Fn] = None
    fallbacks: List[Fn] = []

    for step_node in node.steps:
        if step_node.primary:
            if current_fn is not None:
                steps.append(Step(current_fn, tuple(fallbacks)))
                fallbacks = []
            current_fn = step_node.fn  # type: ignore[assignment]
        else:
            if current_fn is None:
                # Defensive: treat fallback as primary if no primary seen yet.
                current_fn = step_node.fn  # type: ignore[assignment]
            else:
                fallbacks.append(step_node.fn)  # type: ignore[arg-type]

    if current_fn is not None:
        steps.append(Step(current_fn, tuple(fallbacks)))

    return Section(steps=tuple(steps))


def _build_sections_and_principles(
    items: Iterable[StepChain | SectionNode | Fn],
) -> Tuple[
    Dict[Phase, List[Section]],
    Dict[Phase, List[Optional[Principle]]],
    Dict[Phase, PhaseConfig],
]:
    """
    Split incoming DSL objects into Sections, Principles, and PhaseConfig.

    - StepChain → Section + optional Principle, phase derived from chain.phase_key
                  and per-phase config from chain.phase_kwargs.
    - bare Fn   → Section in DEFAULT_PHASE, no Principle, default PhaseConfig.
    """
    sections_by_phase: Dict[Phase, List[Section]] = {
        Phase.SET: [],
        Phase.GET: [],
    }
    principles_by_phase: Dict[Phase, List[Optional[Principle]]] = {
        Phase.SET: [],
        Phase.GET: [],
    }
    phase_cfg_by_phase: Dict[Phase, PhaseConfig] = {}

    for obj in items:
        if isinstance(obj, StepChain):
            # Convert syntax to AST and continue uniformly.
            node = obj.to_node()
            phase_key = node.phase_key
            if not isinstance(phase_key, Phase):
                raise TypeError(
                    f"Codex backend only supports Phase keys of type Phase; got {phase_key!r}"
                )
            phase = phase_key

            sec = _build_section_from_node(node)
            sections_by_phase[phase].append(sec)

            # Semantic token is opaque at DSL level; Codex normalizes it.
            if node.semantic is not None:
                principle = to_principle(node.semantic)
            else:
                principle = None
            principles_by_phase[phase].append(principle)

            # Build a PhaseConfig from the phase_kwargs, but only using
            # fields Codex understands (strict, dest). Other keys are
            # ignored here but preserved in principle/semantics if needed.
            kwargs = node.phase_kwargs or {}
            cfg = PhaseConfig(
                strict=kwargs.get("strict"),
                dest=kwargs.get("dest"),
            )

            prev = phase_cfg_by_phase.get(phase)
            if prev is None:
                phase_cfg_by_phase[phase] = cfg
            else:
                # Small compatibility check: if both specify strict/dest
                # and they differ, raise to avoid silent surprises.
                if (
                    prev.strict is not None
                    and cfg.strict is not None
                    and prev.strict != cfg.strict
                ) or (
                    prev.dest is not None
                    and cfg.dest is not None
                    and prev.dest != cfg.dest
                ):
                    raise ValueError(
                        f"Incompatible PhaseConfig for phase {phase!r}: {prev!r} vs {cfg!r}"
                    )
                # Otherwise keep existing prev (first one wins).
        elif isinstance(obj, SectionNode):
            phase_key = obj.phase_key
            if not isinstance(phase_key, Phase):
                raise TypeError(
                    f"Codex backend only supports Phase keys of type Phase; got {phase_key!r}"
                )
            phase = phase_key
            sec = _build_section_from_node(obj)
            sections_by_phase[phase].append(sec)
            if obj.semantic is not None:
                principle = to_principle(obj.semantic)
            else:
                principle = None
            principles_by_phase[phase].append(principle)
            kwargs = obj.phase_kwargs or {}
            cfg = PhaseConfig(
                strict=kwargs.get("strict"),
                dest=kwargs.get("dest"),
            )
            prev = phase_cfg_by_phase.get(phase)
            if prev is None:
                phase_cfg_by_phase[phase] = cfg
            else:
                if (
                    prev.strict is not None
                    and cfg.strict is not None
                    and prev.strict != cfg.strict
                ) or (
                    prev.dest is not None
                    and cfg.dest is not None
                    and prev.dest != cfg.dest
                ):
                    raise ValueError(
                        f"Incompatible PhaseConfig for phase {phase!r}: {prev!r} vs {cfg!r}"
                    )
        else:
            # Bare function → build synthetic SectionNode then reuse AST→IR path
            phase = DEFAULT_PHASE
            synthetic_node = SectionNode(
                steps=(StepNode(primary=True, fn=obj),),
                semantic=None,
                phase_key=phase,
                phase_kwargs={},
            )
            sec = _build_section_from_node(synthetic_node)
            sections_by_phase[phase].append(sec)
            principles_by_phase[phase].append(None)
            phase_cfg_by_phase.setdefault(phase, PhaseConfig())

    return sections_by_phase, principles_by_phase, phase_cfg_by_phase


# ================================================================
# Section ID numbering
# ================================================================


def assign_section_ids(sections: Sequence[Section]) -> List[str]:
    """
    Number sections in a stable, human-readable way:

        "1", "2", "3", ...

    IDs are not stored in Section; they live in SectionBinding.
    """
    return [str(i) for i in range(1, len(sections) + 1)]


# ================================================================
# High-level: build CodexBinding from DSL
# ================================================================


def build_codex_binding(
    steps: Iterable[StepChain | Fn],
    *,
    domain: str,
    config: CodexConfig,
) -> CodexBinding:
    """
    Build CodexIR + bindings from DSL definitions.

    Input
    -----
    steps:
        Iterable of StepChain | bare functions.

    domain:
        Fully-qualified attribute name for this Codex
        (e.g. "User.email").

    config:
        Codex-level configuration (strict=True/False/None).

    Output
    ------
    CodexBinding:
        - codex: CodexIR (SET/GET PhaseNodes)
        - phases: PhaseBinding with SectionBinding/Principle/IDs
        - config: CodexConfig
        - domain: same as input domain
    """
    sections_by_phase, principles_by_phase, phase_cfg_by_phase = _build_sections_and_principles(
        steps
    )

    phase_nodes: List[PhaseNode] = []
    phase_bindings: List[PhaseBinding] = []

    # Iterate phases in deterministic order: SET then GET.
    for phase in (Phase.SET, Phase.GET):
        sections = sections_by_phase[phase]
        if not sections:
            continue

        # Per-phase config (may be default).
        phase_cfg = phase_cfg_by_phase.get(phase, PhaseConfig())

        # AST node for this phase
        phase_node = PhaseNode(
            phase=phase,
            sections=tuple(sections),
            config=phase_cfg,
        )
        phase_nodes.append(phase_node)

        # Bind IDs and Principles for this phase
        ids = assign_section_ids(sections)
        principles = principles_by_phase[phase]

        section_bindings = tuple(
            SectionBinding(section=sec, id=sid, principle=principle)
            for sec, sid, principle in zip(sections, ids, principles)
        )

        phase_binding = PhaseBinding(
            phase=phase,
            sections=section_bindings,
            config=phase_cfg,
        )
        phase_bindings.append(phase_binding)

    ir = CodexIR(phases=tuple(phase_nodes), config=config)

    binding = CodexBinding(
        codex=ir,
        phases=tuple(phase_bindings),
        config=config,
        domain=domain,
    )
    return binding
