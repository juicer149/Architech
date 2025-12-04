from blueprint.codex.factory import _build_sections_and_principles
from blueprint.dsl.syntax import StepChain
from blueprint.codex import SET
from blueprint.codex.models import Section, Step, Phase


def inc(x):
    return x + 1


def default(x):
    return x


def test_factory_builds_ir_from_ast():
    chain = SET() >> inc << default | "sem"
    sections_by_phase, principles_by_phase, phase_cfg_by_phase = _build_sections_and_principles([chain])

    sections = sections_by_phase[Phase.SET]
    assert len(sections) == 1
    sec = sections[0]
    assert isinstance(sec, Section)
    assert len(sec.steps) == 1
    step = sec.steps[0]
    assert isinstance(step, Step)
    assert step.fn is inc
    assert step.fallbacks == (default,)

    principles = principles_by_phase[Phase.SET]
    assert principles[0] is not None  # semantic normalized

    phase_cfg = phase_cfg_by_phase[Phase.SET]
    assert phase_cfg.strict is None and phase_cfg.dest is None
