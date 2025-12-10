from codex.engine import CodexEngine
from codex.models import CodexConfig, build_codex_spec, Phase, SectionSpec, ClusterSpec, PhaseSpec

# We will indirectly hit _try_section_strict via _run_section in semantic mode.

def bad_primary(x):
    return ValueError("boom")


def test_try_section_strict_returns_error_and_current_in_semantic_mode():
    cluster = ClusterSpec(
        primary=bad_primary,
        fallbacks=(),
        ors=(),
        primary_name="bad_primary",
        fallback_names=(),
        or_names=(),
    )
    section = SectionSpec(phase=Phase.SET, clusters=(cluster,), principle=None)

    # Build spec with a principle in another phase to force semantic auto-mode
    other_cluster = ClusterSpec(
        primary=lambda x: x,
        fallbacks=(),
        ors=(),
        primary_name="noop",
        fallback_names=(),
        or_names=(),
    )
    from codex.semantics import Principle
    from codex.constants import DEFAULT_PRAXIS
    other_section = SectionSpec(phase=Phase.GET, clusters=(other_cluster,), principle=Principle("codex", DEFAULT_PRAXIS))

    base = build_codex_spec(())
    spec = type(base)({
        Phase.SET: PhaseSpec(Phase.SET, (section,)),
        Phase.GET: PhaseSpec(Phase.GET, (other_section,)),
    }, True)

    engine = CodexEngine(spec, CodexConfig(strict=None))
    assert engine.strict is False  # semantic mode

    # Running SET should keep current value on failure in semantic replay
    result = engine.run_phase(Phase.SET, "y")
    assert result == "y"
