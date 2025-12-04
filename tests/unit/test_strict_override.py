from blueprint.codex.factory import build_codex_binding
from blueprint.codex.models import CodexConfig, Phase
from blueprint.codex import SET, GET


def idf(x):
    return x


def test_phase_strict_overrides_codex_config():
    # Codex-level strict=False, but SET(strict=True) should win for that phase
    b = build_codex_binding([
        SET(strict=True) >> idf,
        GET(strict=False) >> idf,
    ], domain="D.x", config=CodexConfig(strict=False))

    set_phase = [p for p in b.phases if p.phase is Phase.SET][0]
    get_phase = [p for p in b.phases if p.phase is Phase.GET][0]

    assert set_phase.config.strict is True
    assert get_phase.config.strict is False
