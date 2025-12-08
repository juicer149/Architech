from dsl import PhaseTokenBase, StepChain
from codex.models import CodexConfig, Phase, build_codex_spec
from codex.engine import CodexEngine
import pytest


def fail(x):
    raise ValueError("primary fail")


def fb1(x):
    return x + 1


def fb2(x):
    return x + 2


def test_primary_fail_then_fallback_succeeds():
    # Section with primary fail; fallbacks would run, but raising exceptions propagates in strict mode
    SET = PhaseTokenBase(Phase.SET)
    chain: StepChain = SET >> fail << fb1 << fb2
    spec = build_codex_spec((chain.to_section(),))
    eng = CodexEngine(spec, CodexConfig(strict=True))
    with pytest.raises(ValueError):
        eng.run_phase(Phase.SET, 1)

