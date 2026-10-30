from pathlib import Path
from typing import ClassVar

from codemind.database.repository import CodeMindRepository
from codemind.graph.dependency import DependencyGraphService
from codemind.parser.service import CodeParser
from codemind.scanner.service import RepositoryScanner


class RepositoryIndexer:
    """Scan, parse, and persist repository source-code metadata."""

    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {".py", ".java"}

    def __init__(
        self,
        scanner=None,
        parser=None,
        repository=None,
        dependency_graph=None,
    ):
        self.scanner = scanner or RepositoryScanner()
        self.parser = parser or CodeParser()
        self.repository = repository or CodeMindRepository()
        self.dependency_graph = dependency_graph or DependencyGraphService()

    def index_repository(self, repository_path: str | Path) -> dict:
        """Index repository metadata and build its dependency graph."""

        root = Path(repository_path).resolve()

        if not root.exists() or not root.is_dir():
            raise ValueError("Repository path must be an existing directory")

        summary = self.scanner.scan(root)

        indexed_files = 0
        skipped_files = 0
        failed_files = 0
        total_symbols = 0
        total_imports = 0
        total_calls = 0
        errors = []

        parsed_files = []

        repository_id = self.repository.save_repository(str(root))

        for file_info in summary.files:
            file_path = Path(file_info.path)

            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                skipped_files += 1
                continue

            absolute_path = root / file_path

            try:
                parsed_file = self.parser.parse_file(absolute_path)
                parsed_files.append(parsed_file)

                indexed_files += 1
                total_symbols += len(parsed_file.symbols)
                total_imports += len(parsed_file.imports)
                total_calls += len(parsed_file.calls)

            except Exception as error:  # noqa: BLE001
                # Record the parsing failure and continue with the next file.
                failed_files += 1
                errors.append(f"{file_info.path}: {error}")

        for parsed_file in parsed_files:
            try:
                self.repository.save_parsed_file(
                    repository_id=repository_id,
                    parsed_file=parsed_file,
                )

            except Exception as error:  # noqa: BLE001
                # Record database failures without stopping the indexing run.
                failed_files += 1
                indexed_files -= 1
                errors.append(f"{parsed_file.file_path}: Database save failed: {error}")

        try:
            self.dependency_graph.build(parsed_files)
            dependency_summary = self.dependency_graph.get_summary()

        except Exception as error:  # noqa: BLE001
            # Preserve indexed metadata if graph construction fails.
            dependency_summary = {}
            errors.append(f"Dependency graph failed: {error}")

        return {
            "repository_path": str(root),
            "total_files": summary.total_files,
            "indexed_files": indexed_files,
            "skipped_files": skipped_files,
            "failed_files": failed_files,
            "total_symbols": total_symbols,
            "total_imports": total_imports,
            "total_calls": total_calls,
            "dependency_summary": dependency_summary,
            "errors": errors,
        }
