from blueprint.codex.factory import build_codex_binding
from blueprint.codex.models import CodexConfig, Phase
from blueprint.codex import SET, GET
from blueprint.pipeline.codex_pipeline import PipelineCompiler


def test_empty_sections_noop():
    b = build_codex_binding([], domain="D.x", config=CodexConfig(strict=True))
    compiler = PipelineCompiler()
    pipes = compiler.build_pipeline(binding=b, panopticon=None)
    assert Phase.SET not in pipes and Phase.GET not in pipes

