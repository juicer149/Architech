from codex.engine import CodexEngine
from codex.models import CodexConfig, build_codex_spec, Phase, SectionSpec, ClusterSpec, PhaseSpec
from codex.semantics import Principle
from codex.constants import DEFAULT_PRAXIS


def primary(x):
    # Primary returns None (no change) when input is fixed
    if x == "fixed":
        return None
    return ValueError("bad input")


def fallback_fix(x):
    # Fallback transforms current into a fixed value
    return "fixed"


def test_primary_none_after_fallback_keeps_fallback_output():
    # Build SectionSpec with primary + fallback
    cluster = ClusterSpec(
        primary=primary,
        fallbacks=(fallback_fix,),
        ors=(),
        primary_name="primary",
        fallback_names=("fallback_fix",),
        or_names=(),
    )
    section = SectionSpec(phase=Phase.SET, clusters=(cluster,), principle=None)
    spec = build_codex_spec(())
    # Manually inject our phase to avoid DSL dependency
    spec = type(spec)({Phase.SET: PhaseSpec(Phase.SET, (section,))}, spec.has_principles)

    engine = CodexEngine(spec, CodexConfig(strict=True))

    result = engine.run_phase(Phase.SET, "bad")
    # Expect the fallback output ("fixed") to be kept when primary returns None
    assert result == "fixed"
