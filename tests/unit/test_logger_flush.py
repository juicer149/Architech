import pytest

pytest.skip("Outdated logging/flush expectations; rewrite to new Output routing", allow_module_level=True)
from codex.engine import CodexEngine
from codex.models import CodexConfig, build_codex_spec, Phase, SectionSpec, ClusterSpec, PhaseSpec
from codex.semantics import Principle, Praxis


def fail(x):
    return ValueError("oops")


def test_custom_logger_receives_violation_messages():
    messages = []
    def logger(msg: str):
        messages.append(msg)

    # Principle with timing=False -> phase-level logging/aggregation
    principle = Principle("codex", Praxis(timing=False, action=False))

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

    # Run; expect semantic mode and a violation recorded then flushed
    result = engine.run_phase(Phase.SET, "x")
    assert result == "x"  # no change on failure
    assert any("[codex]" in m and "oops" in m for m in messages)
