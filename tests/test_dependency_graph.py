from codemind.graph.dependency import DependencyGraphService
from codemind.parser.models import CodeImport, ParsedFile


def make_parsed_file(file_path, imports=None, language="Python"):
    return ParsedFile(
        file_path=file_path,
        language=language,
        symbols=[],
        imports=imports or [],
        calls=[],
        errors=[],
    )


def test_build_dependency_graph():
    parsed_files = [
        make_parsed_file(
            "controller.py",
            [CodeImport(statement="from service import PaymentService", line=1)],
        ),
        make_parsed_file(
            "service.py",
            [CodeImport(statement="from repository import PaymentRepository", line=1)],
        ),
        make_parsed_file("repository.py"),
    ]

    service = DependencyGraphService()
    graph = service.build(parsed_files)

    assert graph.number_of_nodes() == 3
    assert graph.has_edge("controller.py", "service.py")
    assert graph.has_edge("service.py", "repository.py")


def test_get_dependencies():
    parsed_files = [
        make_parsed_file(
            "controller.py",
            [CodeImport(statement="from service import PaymentService", line=1)],
        ),
        make_parsed_file("service.py"),
    ]

    service = DependencyGraphService()
    service.build(parsed_files)

    dependencies = service.get_dependencies("controller.py")

    assert dependencies == ["service.py"]


def test_get_dependents():
    parsed_files = [
        make_parsed_file(
            "controller.py",
            [CodeImport(statement="from service import PaymentService", line=1)],
        ),
        make_parsed_file("service.py"),
    ]

    service = DependencyGraphService()
    service.build(parsed_files)

    dependents = service.get_dependents("service.py")

    assert dependents == ["controller.py"]


def test_get_transitive_impact():
    parsed_files = [
        make_parsed_file(
            "controller.py",
            [CodeImport(statement="from service import PaymentService", line=1)],
        ),
        make_parsed_file(
            "service.py",
            [CodeImport(statement="from repository import PaymentRepository", line=1)],
        ),
        make_parsed_file("repository.py"),
    ]

    service = DependencyGraphService()
    service.build(parsed_files)

    impact = service.get_impact("repository.py")

    assert set(impact) == {"service.py", "controller.py"}


def test_get_summary():
    parsed_files = [
        make_parsed_file(
            "controller.py",
            [CodeImport(statement="from service import PaymentService", line=1)],
        ),
        make_parsed_file("service.py"),
    ]

    service = DependencyGraphService()
    service.build(parsed_files)

    summary = service.get_summary()

    assert summary["total_files"] == 2
    assert summary["total_dependencies"] == 1
    assert summary["is_acyclic"] is True
