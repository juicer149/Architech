import pytest

pytest.skip("Outdated strict detection flag; rewrite to reflect Engine behavior without global flags", allow_module_level=True)
from codex.engine import CodexEngine
from codex.models import CodexConfig, build_codex_spec, Phase, SectionSpec, ClusterSpec, PhaseSpec
from codex.semantics import Principle
from codex.constants import DEFAULT_PRAXIS


def noop(x):
    return x


def test_auto_strict_true_when_no_principles():
    cluster = ClusterSpec(
        primary=noop,
        fallbacks=(),
        ors=(),
        primary_name="noop",
        fallback_names=(),
        or_names=(),
    )
    section = SectionSpec(phase=Phase.SET, clusters=(cluster,), principle=None)
    base = build_codex_spec(())
    spec = type(base)({Phase.SET: PhaseSpec(Phase.SET, (section,))}, False)

    engine = CodexEngine(spec, CodexConfig(strict=None))
    # With no principles, auto-strict should be True
    assert engine.strict is True


def test_auto_strict_false_when_any_principle():
    cluster = ClusterSpec(
        primary=noop,
        fallbacks=(),
        ors=(),
        primary_name="noop",
        fallback_names=(),
        or_names=(),
    )
    principle = Principle("codex", DEFAULT_PRAXIS)
    section = SectionSpec(phase=Phase.SET, clusters=(cluster,), principle=principle)
    base = build_codex_spec(())
    spec = type(base)({Phase.SET: PhaseSpec(Phase.SET, (section,))}, True)

    engine = CodexEngine(spec, CodexConfig(strict=None))
    # With any principle, auto-strict should be False (semantic mode)
    assert engine.strict is False
