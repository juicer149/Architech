from codex.models import Phase, build_codex_spec


def test_empty_sections_noop():
    spec = build_codex_spec(())
    # No phases present when no sections provided
    assert Phase.SET not in spec.phases and Phase.GET not in spec.phases

