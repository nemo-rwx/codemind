from codemind.graph.dependency import DependencyGraphService
from codemind.parser.models import CodeImport, ParsedFile


def make_file(path, imports=None):
    return ParsedFile(
        file_path=path,
        language="python",
        symbols=[],
        imports=[
            CodeImport(statement=statement, line=1) for statement in (imports or [])
        ],
        calls=[],
        errors=[],
    )


def test_analyze_change_finds_direct_and_indirect_dependents():
    files = [
        make_file("controller.py", ["from service import Service"]),
        make_file("service.py", ["from repository import Repository"]),
        make_file("repository.py"),
    ]

    graph = DependencyGraphService()
    graph.build(files)

    result = graph.analyze_change("repository.py")

    assert result["exists"] is True
    assert result["direct_dependents"] == ["service.py"]
    assert set(result["affected_files"]) == {
        "service.py",
        "controller.py",
    }
    assert result["total_affected"] == 2


def test_analyze_change_for_unknown_file():
    graph = DependencyGraphService()

    result = graph.analyze_change("unknown.py")

    assert result["exists"] is False
    assert result["affected_files"] == []
    assert result["total_affected"] == 0
