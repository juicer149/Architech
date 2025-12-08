from dsl import StepChain, PhaseTokenBase
from dsl.nodes import SectionNode, StepNode, ClusterNode
from codex.models import Phase


def f_primary(x):
    return x + 1


def f_fallback(x):
    return x


def test_stepchain_to_node_structure():
    SET = PhaseTokenBase(Phase.SET)
    chain = SET >> f_primary << f_fallback | "semantic-token"
    node = chain.to_section()

    assert isinstance(node, SectionNode)
    assert node.semantic == "semantic-token"
    assert node.phase is Phase.SET
    assert len(node.clusters) == 1
    assert isinstance(node.clusters[0], ClusterNode)
    assert isinstance(node.clusters[0].primary, StepNode)
    assert node.clusters[0].primary.fn is f_primary
    assert len(node.clusters[0].fallbacks) == 1
    assert node.clusters[0].fallbacks[0].fn is f_fallback


def test_get_phase_token_to_node():
    GET = PhaseTokenBase(Phase.GET)
    chain = GET >> f_primary
    node = chain.to_section()
    assert isinstance(node, SectionNode)
    assert node.phase is Phase.GET
