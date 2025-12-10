import pytest

from codex.engine import CodexEngine
from codex.models import CodexConfig, build_codex_spec, Phase, SectionSpec, ClusterSpec, PhaseSpec


def primary(x):
    return ValueError("fail")


def fb_fail(x):
    return ValueError("still bad")


def or_fail(x):
    return ValueError("or bad")


def noop(x):
    return None


def test_mixed_fallbacks_and_ors_raises_runtime_error():
    # Construct an invalid ClusterSpec mixing fallbacks and ors to trigger error path
    cluster = ClusterSpec(
        primary=noop,
        fallbacks=(fb_fail,),
        ors=(or_fail,),
        primary_name="noop",
        fallback_names=("fb_fail",),
        or_names=("or_fail",),
    )
    section = SectionSpec(phase=Phase.SET, clusters=(cluster,), principle=None)
    base = build_codex_spec(())
    spec = type(base)({Phase.SET: PhaseSpec(Phase.SET, (section,))}, False)

    engine = CodexEngine(spec, CodexConfig(strict=True))
    with pytest.raises(RuntimeError):
        engine.run_phase(Phase.SET, "x")


def test_or_all_fail_propagates_last_exception():
    # Primary and all ORs fail -> last_exc path
    cluster = ClusterSpec(
        primary=primary,
        fallbacks=(),
        ors=(or_fail,),
        primary_name="primary",
        fallback_names=(),
        or_names=("or_fail",),
    )
    section = SectionSpec(phase=Phase.SET, clusters=(cluster,), principle=None)
    base = build_codex_spec(())
    spec = type(base)({Phase.SET: PhaseSpec(Phase.SET, (section,))}, False)

    engine = CodexEngine(spec, CodexConfig(strict=True))
    with pytest.raises(ValueError) as ei:
        engine.run_phase(Phase.SET, "x")
    assert "or bad" in str(ei.value) or "fail" in str(ei.value)


def test_flush_raise_path_aggregates_and_raises():
    from codex.semantics import Principle, Praxis

    def bad(x):
        return ValueError("agg raise")

    # Two sections, both raise, action=True so flush raises aggregated message
    p = Principle("error", Praxis(timing=False, action=True))

    cluster = ClusterSpec(
        primary=bad,
        fallbacks=(),
        ors=(),
        primary_name="bad",
        fallback_names=(),
        or_names=(),
    )
    s1 = SectionSpec(phase=Phase.SET, clusters=(cluster,), principle=p)
    s2 = SectionSpec(phase=Phase.SET, clusters=(cluster,), principle=p)

    base = build_codex_spec(())
    spec = type(base)({Phase.SET: PhaseSpec(Phase.SET, (s1, s2))}, True)

    engine = CodexEngine(spec, CodexConfig(strict=None))
    with pytest.raises(RuntimeError) as ei:
        engine.run_phase(Phase.SET, "v")
    text = str(ei.value)
    assert text.count("agg raise") == 2
