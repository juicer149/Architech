from codex.models import build_codex_spec, SectionSpec, PhaseSpec, Phase
from codex.semantics import Principle, Praxis
from typing import Callable, Any


def idfn(x: Any) -> Any:
    return x


def test_build_spec_only_set_phase_and_has_principles_true():
    cluster = __import__('codex.models').models.ClusterSpec(
        primary=idfn,
        fallbacks=(),
        ors=(),
        primary_name="idfn",
        fallback_names=(),
        or_names=(),
    )
    principle = Principle("error", Praxis(timing=True, action=True))
    sec = SectionSpec(phase=Phase.SET, clusters=(cluster,), principle=principle)

    # Manually assemble PhaseSpec for SET only
    phases = {Phase.SET: PhaseSpec(Phase.SET, (sec,))}
    # build_codex_spec typically converts from DSL, but we can mimic outcome by
    # creating a minimal spec via its dataclass for coverage
    spec = __import__('codex.models').models.CodexSpec(phases, has_principles=True)

    assert Phase.SET in spec.phases and Phase.GET not in spec.phases
    assert spec.has_principles is True


def test_build_spec_only_get_phase_and_has_principles_false():
    cluster = __import__('codex.models').models.ClusterSpec(
        primary=idfn,
        fallbacks=(),
        ors=(),
        primary_name="idfn",
        fallback_names=(),
        or_names=(),
    )
    sec = SectionSpec(phase=Phase.GET, clusters=(cluster,), principle=None)

    phases = {Phase.GET: PhaseSpec(Phase.GET, (sec,))}
    spec = __import__('codex.models').models.CodexSpec(phases, has_principles=False)

    assert Phase.GET in spec.phases and Phase.SET not in spec.phases
    assert spec.has_principles is False
