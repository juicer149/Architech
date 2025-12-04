from blueprint.codex.factory import build_codex_binding
from blueprint.codex.models import CodexConfig, Phase
from blueprint.codex import SET


def inc(x):
    return x + 1


def dbl(x):
    return x * 2


def test_multiple_primary_steps_chain():
    # Two primaries become two IR Steps in one Section
    chain = SET(strict=True) >> inc >> dbl
    b = build_codex_binding([chain], domain="D.x", config=CodexConfig(strict=True))
    sec = [p for p in b.phases if p.phase is Phase.SET][0].sections[0].section
    # Expect two steps
    assert len(sec.steps) == 2
    # Manual run: (x+1) then (*2)
    cur = 1
    cur = sec.steps[0].fn(cur)
    cur = sec.steps[1].fn(cur)
    assert cur == 4

