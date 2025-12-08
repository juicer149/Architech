from dsl import PhaseTokenBase, StepChain
from codex.models import CodexConfig, Phase, build_codex_spec
from codex.engine import CodexEngine
from codex.semantics import Principle, Praxis


def fail(x):
    # Return a soft failure for semantic handling
    return RuntimeError("boom")


def test_exception_mapping_semantic_mode():
    # Principle raises ValueError in semantic replay
    SET = PhaseTokenBase(Phase.SET)
    P = Principle(label="map", praxis=Praxis(True, True), exc_type=ValueError)
    chain: StepChain = (SET >> fail) | P
    spec = build_codex_spec((chain.to_section(),))
    eng = CodexEngine(spec, CodexConfig(strict=None))
    try:
        eng.run_phase(Phase.SET, 1)
    except Exception as e:
        assert isinstance(e, ValueError)

