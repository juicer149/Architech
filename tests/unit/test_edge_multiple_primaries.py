from dsl import PhaseTokenBase, StepChain
from dsl.nodes import SectionNode
from codex.models import Phase


def inc(x):
    return x + 1


def dbl(x):
    return x * 2


def test_multiple_primary_steps_chain():
    # Two primaries become two StepNodes in one Cluster within a Section
    SET = PhaseTokenBase(Phase.SET)
    chain: StepChain = SET >> inc >> dbl
    node: SectionNode = chain.to_section()
    # Each primary becomes its own cluster in current DSL design
    assert len(node.clusters) == 2
    cur = 1
    cur = node.clusters[0].primary.fn(cur)
    cur = node.clusters[1].primary.fn(cur)
    assert cur == 4

