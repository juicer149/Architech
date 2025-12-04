from blueprint.codex.factory import build_codex_binding
from blueprint.codex.models import CodexConfig, Phase
from blueprint.codex.codex import Codex
from blueprint.codex import SET, GET
from blueprint.pipeline.codex_pipeline import PipelineCompiler
from control.panopticon import Panopticon
from control.capture.capture import Capture


def inc(x):
    return x + 1


def idf(x):
    return x


def test_compile_and_run_strict_interpreted():
    # No semantic tokens → auto strict mode
    b = build_codex_binding([SET() >> inc, GET() >> idf], domain="D.x", config=CodexConfig(strict=None))
    # Build pipelines using public API
    compiler = PipelineCompiler()
    pipelines = compiler.build_pipeline(binding=b, panopticon=None)

    set_pipeline = pipelines[Phase.SET][0]
    get_pipeline = pipelines[Phase.GET][0]

    # Run SET then GET
    value = set_pipeline(1)
    assert value == 2
    value = get_pipeline(value)
    assert value == 2
