from dsl import PhaseTokenBase
from codex.models import CodexConfig, Phase, build_codex_spec
from codex.engine import CodexEngine
from codex import WARN


def idf(x):
    return x


def test_auto_detect_semantic_mode_with_principle():
    SET = PhaseTokenBase(Phase.SET)
    # annotate section with a Principle to trigger semantic mode when strict=None
    set_section = (SET >> idf | WARN).to_section()
    spec = build_codex_spec((set_section,))
    eng = CodexEngine(spec, CodexConfig(strict=None))
    assert eng.strict is False
