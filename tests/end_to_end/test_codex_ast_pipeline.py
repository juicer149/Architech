from dsl import PhaseTokenBase, StepChain
from codex.models import Phase, build_codex_spec


def lower(x: str) -> str:
    return x.lower()


def fallback_identity(x):
    return x


def test_codex_builds_binding_with_ast_flow():
    # Build DSL using syntax
    SET = PhaseTokenBase(Phase.SET)
    GET = PhaseTokenBase(Phase.GET)

    set_chain: StepChain = SET >> lower << fallback_identity | "sem-set"
    get_chain: StepChain = GET >> lower | "sem-get"

    spec = build_codex_spec((set_chain.to_section(), get_chain.to_section()))

    # SET
    set_phase = spec.phases[Phase.SET]
    assert len(set_phase.sections) == 1
    # GET
    get_phase = spec.phases[Phase.GET]
    assert len(get_phase.sections) == 1
