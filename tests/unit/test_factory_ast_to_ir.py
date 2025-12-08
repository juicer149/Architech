from dsl import PhaseTokenBase, StepChain
from dsl.nodes import SectionNode, StepNode
from codex.models import Phase, build_codex_spec, section_from_dsl
from codex.semantics import Principle


def inc(x):
    return x + 1


def default(x):
    return x


def test_ir_builds_from_dsl_section():
    SET = PhaseTokenBase(Phase.SET)
    chain: StepChain = SET >> inc << default | "sem"
    node: SectionNode = chain.to_section()
    sec_ir = section_from_dsl(node)
    assert sec_ir.phase is Phase.SET
    assert len(sec_ir.clusters) == 1
    cl = sec_ir.clusters[0]
    assert isinstance(cl.primary, type(inc)) or callable(cl.primary)
    assert cl.primary_name == inc.__name__
    assert cl.fallbacks and cl.fallback_names[0] == default.__name__

    spec = build_codex_spec((node,))
    assert Phase.SET in spec.phases
