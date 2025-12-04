from blueprint.codex.factory import build_codex_binding
from blueprint.codex.models import CodexConfig, Phase
from blueprint.codex import SET, GET


def idf(x):
    return x


def test_phase_config_dest_metadata():
    b = build_codex_binding([SET(dest="other_field") >> idf, GET() >> idf], domain="User.attr", config=CodexConfig(strict=None))

    # PhaseBinding should carry dest metadata
    set_phase_binding = [p for p in b.phases if p.phase is Phase.SET][0]
    assert set_phase_binding.config.dest == "other_field"

    # PhaseNode in IR should also carry dest in its config
    set_phase_node = [p for p in b.codex.phases if p.phase is Phase.SET][0]
    assert set_phase_node.config.dest == "other_field"

    # And GET phase should not have dest
    get_phase_binding = [p for p in b.phases if p.phase is Phase.GET][0]
    assert get_phase_binding.config.dest is None
