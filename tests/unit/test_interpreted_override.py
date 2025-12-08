from dsl import PhaseTokenBase
from codex.models import CodexConfig, Phase, build_codex_spec
from codex.engine import CodexEngine


def idf(x):
    return x


def test_config_strict_true_runs_strict_mode():
    SET = PhaseTokenBase(Phase.SET)
    GET = PhaseTokenBase(Phase.GET)
    spec = build_codex_spec(((SET >> idf).to_section(),))
    eng = CodexEngine(spec, CodexConfig(strict=True))
    assert eng.strict is True

def test_config_strict_false_runs_semantic_mode():
    SET = PhaseTokenBase(Phase.SET)
    spec = build_codex_spec(((SET >> idf).to_section(),))
    eng = CodexEngine(spec, CodexConfig(strict=False))
    assert eng.strict is False
