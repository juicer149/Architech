from dsl import PhaseTokenBase, StepChain
from codex.models import CodexConfig, Phase, build_codex_spec
from codex.engine import CodexEngine


def inc(x):
    return x + 1


def idf(x):
    return x


def test_compile_and_run_strict_interpreted():
    # Construct phase tokens for DSL from Codex Phase enum
    SET = PhaseTokenBase(Phase.SET)
    GET = PhaseTokenBase(Phase.GET)

    # No semantic tokens → auto strict mode
    set_chain: StepChain = SET >> inc
    get_chain: StepChain = GET >> idf

    spec = build_codex_spec((set_chain.to_section(), get_chain.to_section()))
    engine = CodexEngine(spec, CodexConfig(strict=None))

    # Run SET then GET via engine
    value = engine.run_phase(Phase.SET, 1)
    assert value == 2
    value = engine.run_phase(Phase.GET, value)
    assert value == 2
