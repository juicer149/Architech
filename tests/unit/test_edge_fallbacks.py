from blueprint.codex.factory import build_codex_binding
from blueprint.codex.models import CodexConfig, Phase
from blueprint.codex import SET, GET
from blueprint.pipeline.codex_pipeline import PipelineCompiler
import pytest


def fail(x):
    raise ValueError("primary fail")


def fb1(x):
    return x + 1


def fb2(x):
    return x + 2


def test_primary_fail_then_fallback_succeeds():
    # Section with primary fail; fallback succeeds then retry primary
    chain = SET(strict=True) >> fail << fb1 << fb2
    b = build_codex_binding([chain], domain="D.x", config=CodexConfig(strict=True))
    compiler = PipelineCompiler()
    pipes = compiler.build_pipeline(binding=b, panopticon=None)
    stage = pipes[Phase.SET][0]
    # Current semantics: fallback(s) run; primary retried; if it still fails,
    # the last error propagates
    with pytest.raises(ValueError):
        stage(1)

