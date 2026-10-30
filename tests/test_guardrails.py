import pytest

from codemind.agent.guardrails import (
    GuardrailError,
    GuardrailService,
)


@pytest.fixture
def repository(tmp_path):
    (tmp_path / "sample.py").write_text(
        "def hello():\n    return 'hello'\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def guardrails():
    return GuardrailService()


def test_rejects_unknown_tool(guardrails, repository):
    with pytest.raises(GuardrailError):
        guardrails.validate_tool_call("delete_file", "sample.py", str(repository))


def test_rejects_path_outside_repository(guardrails, repository):
    with pytest.raises(GuardrailError):
        guardrails.validate_tool_call(
            "analyze_change", "../outside.py", str(repository)
        )


def test_rejects_absolute_path(guardrails, repository):
    with pytest.raises(GuardrailError):
        guardrails.validate_tool_call(
            "analyze_change",
            str(repository / "sample.py"),
            str(repository),
        )


def test_accepts_valid_source_request(guardrails, repository):
    result = guardrails.validate_tool_call(
        "get_source",
        '{"file_path":"sample.py","start_line":1,"end_line":2}',
        str(repository),
    )

    assert result["file_path"] == "sample.py"
    assert result["start_line"] == 1
    assert result["end_line"] == 2


def test_rejects_excessive_source_range(guardrails, repository):
    with pytest.raises(GuardrailError):
        guardrails.validate_tool_call(
            "get_source",
            '{"file_path":"sample.py","start_line":1,"end_line":501}',
            str(repository),
        )


def test_rejects_oversized_input(guardrails, repository):
    with pytest.raises(GuardrailError):
        guardrails.validate_tool_call(
            "search_symbols",
            "x" * 2001,
            str(repository),
        )


def test_rejects_invalid_line_numbers(guardrails, repository):
    with pytest.raises(GuardrailError):
        guardrails.validate_tool_call(
            "get_source",
            '{"file_path":"sample.py","start_line":0,"end_line":2}',
            str(repository),
        )
