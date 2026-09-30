import pytest

pytest.skip("Outdated test; rewrite for Engine None-as-pass-through semantics", allow_module_level=True)
from codex.engine import CodexEngine
from codex.models import CodexConfig, build_codex_spec, Phase, SectionSpec, ClusterSpec, PhaseSpec


def primary_fail(x):
    return ValueError("p fail")


def or_none(x):
    # OR returns None meaning success/no change
    return None


def test_or_none_returns_current():
    cluster = ClusterSpec(
        primary=primary_fail,
        fallbacks=(),
        ors=(or_none,),
        primary_name="primary_fail",
        fallback_names=(),
        or_names=("or_none",),
    )
    section = SectionSpec(phase=Phase.SET, clusters=(cluster,), principle=None)
    base = build_codex_spec(())
    spec = type(base)({Phase.SET: PhaseSpec(Phase.SET, (section,))}, False)

    engine = CodexEngine(spec, CodexConfig(strict=True))
    out = engine.run_phase(Phase.SET, "cur")
    assert out == "cur"
