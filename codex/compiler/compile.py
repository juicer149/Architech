# =============================================================================
# architech/codex/compiler/compile.py
# =============================================================================
"""
(8) Compiler — DSL Section -> Codex IR.

Input
-----
- dsl.Section (phase, clusters, semantic)

Output
------
- dict[Phase, PhasePlan]

Rules
-----
- Multiple Sections may share the same Phase.
  Their Nodes append into the same Pipeline in order.
- Semantic merging is "last wins" per channel:
  - write Output (is_exception=False)
  - exc Output   (is_exception=True)

The compiler enforces cluster invariants:
- cluster[0] must be PRIMARY
- remaining steps must be homogeneous FALLBACK or homogeneous OR
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from dsl import Relation, Section

from ..ir.contract import CODEX_CONTRACT, CodexIRContract
from ..ir.node import Node, StepFn
from ..ir.output import Output
from ..ir.phase import Phase
from ..ir.pipeline import Pipeline
from ..ir.plan import PhasePlan


# ---------------------------------------------------------------------------
# Semantic handling
# ---------------------------------------------------------------------------

def _split_semantic(
    semantic: Any,
) -> tuple[Optional[Output], Optional[Output]]:
    """
    Split DSL semantic into (write_output, exc_output).

    Supported semantic tokens
    -------------------------
    - None
    - Output
    - Iterable of Output (list / tuple / set)

    Rules
    -----
    - Output.is_exception determines channel
    - last Output per channel wins
    """
    if semantic is None:
        return None, None

    write_out: Optional[Output] = None
    exc_out: Optional[Output] = None

    def process_one(item: Any) -> None:
        nonlocal write_out, exc_out

        if item is None:
            return

        if isinstance(item, Output):
            if item.is_exception:
                exc_out = item
            else:
                write_out = item
            return

        raise TypeError(
            f"Unsupported semantic token: {item!r} (type={type(item)!r})"
        )

    if isinstance(semantic, (list, tuple, set)):
        for item in semantic:
            process_one(item)
    else:
        process_one(semantic)

    return write_out, exc_out


# ---------------------------------------------------------------------------
# Node construction
# ---------------------------------------------------------------------------

def _build_node(cluster, *, contract: CodexIRContract) -> Node:
    if not cluster:
        raise ValueError("Empty cluster in DSL Section; this should not happen.")

    first = cluster[0]

    if first.relation is not Relation.PRIMARY:
        raise ValueError(
            "Cluster must start with PRIMARY step; "
            f"got {first.relation!r} instead."
        )

    value = first.value

    if not contract.step_predicate(value):
        raise TypeError(
            f"Codex step must be callable, got {value!r} "
            f"(type={type(value).__name__})"
        )

    primary: StepFn = value

    rest = cluster[1:]
    fallbacks: Tuple[StepFn, ...] = ()
    ors: Tuple[StepFn, ...] = ()

    if rest:
        mode = rest[0].relation

        if mode is Relation.FALLBACK:
            for t in rest:
                if t.relation is not Relation.FALLBACK:
                    raise ValueError(
                        "Cluster mixes FALLBACK with other relations; not allowed."
                    )
                if not contract.step_predicate(t.value):
                    raise TypeError(
                        f"Fallback step must be callable, got {t.value!r}"
                    )
            fallbacks = tuple(t.value for t in rest)

        elif mode is Relation.OR:
            for t in rest:
                if t.relation is not Relation.OR:
                    raise ValueError(
                        "Cluster mixes OR with other relations; not allowed."
                    )
                if not contract.step_predicate(t.value):
                    raise TypeError(
                        f"OR-step must be callable, got {t.value!r}"
                    )
            ors = tuple(t.value for t in rest)

        else:
            raise ValueError(
                f"Unexpected relation {mode!r} in cluster; "
                f"expected FALLBACK or OR."
            )

    return Node(fn=primary, fallbacks=fallbacks, ors=ors)


# ---------------------------------------------------------------------------
# Public compiler entrypoint
# ---------------------------------------------------------------------------

def compile_sections(
    sections: Tuple[Section, ...],
    *,
    contract: CodexIRContract = CODEX_CONTRACT,
) -> Dict[Phase, PhasePlan]:
    """
    Compile DSL Sections into PhasePlans.
    """
    plans: Dict[Phase, PhasePlan] = {}

    for sec in sections:
        try:
            phase = Phase(sec.phase)
        except Exception as exc:
            raise TypeError(
                f"Unsupported phase key in Section: {sec.phase!r}"
            ) from exc

        write_out, exc_out = _split_semantic(sec.semantic)

        nodes: List[Node] = [
            _build_node(cluster, contract=contract)
            for cluster in sec.clusters
        ]

        if phase in plans:
            plan = plans[phase]
            plan.pipeline.nodes.extend(nodes)

            if write_out is not None:
                plan.write = write_out
            if exc_out is not None:
                plan.exc = exc_out

        else:
            plans[phase] = PhasePlan(
                phase=phase,
                pipeline=Pipeline(nodes=nodes),
                write=write_out,
                exc=exc_out,
            )

    return plans
