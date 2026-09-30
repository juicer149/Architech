from codex.compiler.compile import compile_sections


def test_compile_with_no_sections_returns_empty_plan_dict():
    plans = compile_sections(())
    assert isinstance(plans, dict)
    assert plans == {}
