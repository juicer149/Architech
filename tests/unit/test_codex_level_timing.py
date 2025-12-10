from codex.engine import CodexEngine
from codex.models import CodexConfig, build_codex_spec, Phase, SectionSpec, ClusterSpec, PhaseSpec
from codex.semantics import Principle, Praxis


def fail(x):
    return ValueError("later")


def test_codex_level_timing_flushes_at_end():
    # timing=None -> codex-level
    principle = Principle("codex", Praxis(timing=None, action=False))

    cluster = ClusterSpec(
        primary=fail,
        fallbacks=(),
        ors=(),
        primary_name="fail",
        fallback_names=(),
        or_names=(),
    )
    section_set = SectionSpec(phase=Phase.SET, clusters=(cluster,), principle=principle)

    base = build_codex_spec(())
    spec = type(base)({Phase.SET: PhaseSpec(Phase.SET, (section_set,))}, True)

    messages = []
    def logger(msg: str):
        messages.append(msg)

    engine = CodexEngine(spec, CodexConfig(strict=None, logger=logger))

    # Run phase: expect result unchanged, message logged at codex flush
    out = engine.run_phase(Phase.SET, "z")
    assert out == "z"
    assert any("later" in m for m in messages)
