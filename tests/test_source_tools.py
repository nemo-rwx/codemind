import pytest

from codemind.agent.tools.source_tools import SourceCodeTools


def test_get_source(tmp_path):
    source_file = tmp_path / "example.py"

    source_file.write_text(
        "def hello():\n    return 'Hello'\n",
        encoding="utf-8",
    )

    tools = SourceCodeTools()

    result = tools.get_source(
        repository_path=tmp_path,
        file_path="example.py",
        start_line=1,
        end_line=2,
    )

    assert result["file_path"] == "example.py"
    assert result["source_code"] == ("def hello():\n    return 'Hello'")


def test_rejects_path_outside_repository(tmp_path):
    tools = SourceCodeTools()

    with pytest.raises(ValueError, match="outside"):
        tools.get_source(
            repository_path=tmp_path,
            file_path="../secret.txt",
            start_line=1,
            end_line=1,
        )


def test_rejects_invalid_line_range(tmp_path):
    tools = SourceCodeTools()

    with pytest.raises(ValueError, match="Invalid"):
        tools.get_source(
            repository_path=tmp_path,
            file_path="example.py",
            start_line=5,
            end_line=2,
        )


def test_rejects_missing_file(tmp_path):
    tools = SourceCodeTools()

    with pytest.raises(FileNotFoundError):
        tools.get_source(
            repository_path=tmp_path,
            file_path="missing.py",
            start_line=1,
            end_line=2,
        )
