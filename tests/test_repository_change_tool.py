from codemind.agent.tools.repository_tools import RepositoryTools


class FakeScanner:
    def scan(self, root):
        from types import SimpleNamespace

        return SimpleNamespace(
            files=[
                SimpleNamespace(path="controller.py", extension=".py"),
                SimpleNamespace(path="service.py", extension=".py"),
                SimpleNamespace(path="repository.py", extension=".py"),
            ]
        )


class FakeParser:
    def parse_file(self, path):
        from codemind.parser.models import CodeImport, ParsedFile

        imports = {
            "controller.py": ["from service import Service"],
            "service.py": ["from repository import Repository"],
            "repository.py": [],
        }

        return ParsedFile(
            file_path=str(path),
            language="python",
            symbols=[],
            imports=[CodeImport(statement=item, line=1) for item in imports[path.name]],
            calls=[],
            errors=[],
        )


def test_repository_tool_analyzes_change(tmp_path):
    for filename in (
        "controller.py",
        "service.py",
        "repository.py",
    ):
        (tmp_path / filename).write_text(
            "# test file",
            encoding="utf-8",
        )

    tools = RepositoryTools(
        scanner=FakeScanner(),
        parser=FakeParser(),
    )

    result = tools.analyze_change(
        repository_path=tmp_path,
        file_path="repository.py",
    )

    assert result["exists"] is True
    assert result["direct_dependents"] == ["service.py"]
    assert set(result["affected_files"]) == {
        "service.py",
        "controller.py",
    }
    assert result["total_affected"] == 2
