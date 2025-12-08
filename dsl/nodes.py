# ================================================================
# architech/dsl/nodes.py
# ================================================================
"""
Pure structural DSL nodes independent of any specific backend.

These nodes form a small AST-like model that backends (such as Codex)
can consume and turn into their own IR and executable pipelines.

Hierarchy
---------

    SectionNode
        → phase: DSLPhaseKey
        → clusters: ClusterNode[]

    ClusterNode
        → primary: StepNode
        → fallbacks: StepNode[]

    StepNode
        → fn: StepFn

Semantics
---------

The DSL itself is *semantics-free*:

    - It does not know what a "Principle" is.
    - It does not interpret "semantic tokens".
    - It does not decide control flow or validation semantics.

Instead, SectionNode simply holds an opaque `semantic` attribute
(backends may use it as a Principle/Praxis token, label, policy, etc.).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Tuple

from .protocol import DSLPhaseKey, StepFn


@dataclass(frozen=True, slots=True)
class StepNode:
    """Leaf node representing a single callable pipeline step."""
    # om man då inte har StepFn definierad som callable
    # hade dsl kunnat vara helt oberoende av implementation?
    # att i dsl så är detta bara step: Any
    fn: StepFn
    # step: Step


@dataclass(frozen=True, slots=True)
class ClusterNode:
# @dataclass(frozen=True, slots=True)
# class SequenceNode:
    """
    A cluster of one primary step with zero or more fallback steps.

    Backends define what “failure” means for primary steps (returning an
    Exception, raising, sentinel value etc.). The DSL only expresses structure.
    """
    primary: StepNode
    # byta namn på fallbacks till secondary eller alternatives? 
    # alternatives låter mer neutralt och kan då användas av ex nya implementeringen av:
    # or dvs SET >> f1 | f2 @ ERROR
    # alternativt om för or att man byter primary att vara en Tuple[StepNode, ...]
    # sedan hör det till backend att applicera vad nu en step är, som i codex är en callable
    # via att låta primary istället vara Tuple[StepNode, ...], kanske inte ens behöver 
    # En klass för StepNode då, utan att användaren kan ange vad en Step är,
    # cluster är därmed antingen ett step eller flera steps.
    # dsl skulle ansvara då endast logik som ">>", "<<", "|" och "@" och hur det
    # hör till varandra för att skapa ett cluster av steps, dvs att >> betyder ett nytt 
    # cluster, dvs en ny tuple innehållande minst ett step, och alternativt
    # flera steps i en tuple, och beroende på om den använder "<<" eller "|" avgör
    # relationen mellan steppen i tuplen. >> betyder alltså alltid nytt cluster.
    # och @ betyder alltid att inga fler cluster efter detta för denna phase/section, och att
    # @ ger metadata/rules till alla clusters i den sectionen.
    fallbacks: Tuple[StepNode, ...] = ()

    #ny:
    # primary: Step
    # or: Tuple[Step, ...] = ()
    # fallbacks: Tuple[Step, ...] = ()


@dataclass(frozen=True, slots=True)
class SectionNode:
    """
    A phase-specific chain of clusters with an optional semantic token.

    Example:

        SET >> f1 << fb1 << fb2 >> f2 | semantic_token

    Becomes:

        SectionNode(
            phase=SET.key,
            clusters=[
                ClusterNode(primary=f1, fallbacks=[fb1, fb2]),
                ClusterNode(primary=f2)
            ],
            semantic=semantic_token,
        )

    The DSL does not interpret `semantic`. Backends are free to.
    """
    phase: DSLPhaseKey
    clusters: Tuple[ClusterNode, ...]
    semantic: Any | None = None
