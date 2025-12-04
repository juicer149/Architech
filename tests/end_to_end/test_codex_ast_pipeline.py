from blueprint.codex.codex import Codex
from blueprint.codex.constants import DEFAULT_PHASE
from blueprint.codex.factory import build_codex_binding
from blueprint.codex.models import CodexConfig
from blueprint.codex import SET, GET


def lower(x: str) -> str:
    return x.lower()


def fallback_identity(x):
    return x


def test_codex_builds_binding_with_ast_flow():
    # Build DSL using syntax
    set_chain = SET(strict=True) >> lower << fallback_identity | "sem-set"
    get_chain = GET(dest="address") >> lower | "sem-get"

    binding = build_codex_binding([set_chain, get_chain], domain="User.email", config=CodexConfig(strict=None))

    assert binding.domain == "User.email"
    assert binding.codex.config.strict is None
    # SET
    set_phase = [p for p in binding.codex.phases if p.phase.name == "SET"][0]
    assert len(set_phase.sections) == 1
    # GET
    get_phase = [p for p in binding.codex.phases if p.phase.name == "GET"][0]
    assert len(get_phase.sections) == 1
