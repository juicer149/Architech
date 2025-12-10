from codex.models import build_codex_spec


def test_build_empty_spec_has_no_phases_and_no_principles():
    spec = build_codex_spec(())
    assert spec.phases == {}
    assert spec.has_principles is False
