from blueprint.codex.factory import build_codex_binding
from blueprint.codex.models import CodexConfig, Phase
from blueprint.codex import SET
from blueprint.pipeline.codex_pipeline import PipelineCompiler
from control.config import Principle


def fail(x):
    raise RuntimeError("boom")


def test_exception_mapping_strict_mode():
    # Attach a principle with exc_type mapping (simulated via a simple principle)
    P = Principle(label="map", praxis=0, effect=0, exc_type=ValueError)
    chain = (SET(strict=True) >> fail) | P
    b = build_codex_binding([chain], domain="D.x", config=CodexConfig(strict=True))
    compiler = PipelineCompiler()
    stage = compiler.build_pipeline(binding=b, panopticon=None)[Phase.SET][0]
    try:
        stage(1)
    except Exception as e:
        assert isinstance(e, ValueError)

