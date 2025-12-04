from blueprint.dsl.syntax import StepChain
from blueprint.codex import SET, GET
from blueprint.dsl.nodes import SectionNode, StepNode


def f_primary(x):
    return x + 1


def f_fallback(x):
    return x


def test_stepchain_to_node_structure():
    chain = SET(strict=True) >> f_primary << f_fallback | "semantic-token"
    node = chain.to_node()

    assert isinstance(node, SectionNode)
    assert node.semantic == "semantic-token"
    assert node.phase_kwargs == {"strict": True}
    assert len(node.steps) == 2
    assert isinstance(node.steps[0], StepNode)
    assert node.steps[0].primary is True
    assert node.steps[0].fn is f_primary
    assert node.steps[1].primary is False
    assert node.steps[1].fn is f_fallback


def test_get_phase_token_to_node():
    chain = GET(dest="address") >> f_primary
    node = chain.to_node()
    assert isinstance(node, SectionNode)
    assert node.phase_kwargs == {"dest": "address"}
