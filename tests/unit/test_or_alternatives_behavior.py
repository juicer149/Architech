from codex.engine import CodexEngine
from codex.models import CodexConfig, build_codex_spec, Phase, SectionSpec, ClusterSpec, PhaseSpec


def fail(x):
    return ValueError("fail")


def alt_ok(x):
    return f"alt:{x}"


def test_or_alternatives_success_order():
    # primary fails, first OR succeeds
    cluster = ClusterSpec(
        primary=fail,
        fallbacks=(),
        ors=(alt_ok,),
        primary_name="fail",
        fallback_names=(),
        or_names=("alt_ok",),
    )
    section = SectionSpec(phase=Phase.SET, clusters=(cluster,), principle=None)
    base = build_codex_spec(())
    spec = type(base)({Phase.SET: PhaseSpec(Phase.SET, (section,))}, False)

    engine = CodexEngine(spec, CodexConfig(strict=True))
    result = engine.run_phase(Phase.SET, "x")
    assert result == "alt:x"
