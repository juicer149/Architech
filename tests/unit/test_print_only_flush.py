from codex.engine import CodexEngine
from codex.models import CodexConfig, build_codex_spec, Phase, SectionSpec, ClusterSpec, PhaseSpec
from codex.semantics import Principle, Praxis


def fail(x):
    return ValueError("msg")


def test_print_only_no_raise_and_logs_messages():
    messages = []
    def logger(m: str):
        messages.append(m)

    principle = Principle("warn", Praxis(timing=False, action=False))

    cluster = ClusterSpec(
        primary=fail,
        fallbacks=(),
        ors=(),
        primary_name="fail",
        fallback_names=(),
        or_names=(),
    )
    section = SectionSpec(phase=Phase.SET, clusters=(cluster,), principle=principle)
    base = build_codex_spec(())
    spec = type(base)({Phase.SET: PhaseSpec(Phase.SET, (section,))}, True)

    engine = CodexEngine(spec, CodexConfig(strict=None, logger=logger))

    out = engine.run_phase(Phase.SET, "x")
    assert out == "x"
    assert messages and any("warn" in m and "msg" in m for m in messages)
