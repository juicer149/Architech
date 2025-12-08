from dsl import PhaseTokenBase
from codex.models import Phase, build_codex_spec


def idf(x):
    return x


def test_phase_sections_present_without_dest_metadata():
    SET = PhaseTokenBase(Phase.SET)
    GET = PhaseTokenBase(Phase.GET)
    spec = build_codex_spec(((SET >> idf).to_section(), (GET >> idf).to_section()))

    # Phases exist with sections; no dest metadata in new design
    assert Phase.SET in spec.phases
    assert Phase.GET in spec.phases
    assert len(spec.phases[Phase.SET].sections) == 1
    assert len(spec.phases[Phase.GET].sections) == 1
