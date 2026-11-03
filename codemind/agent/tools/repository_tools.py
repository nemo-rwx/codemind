from pathlib import Path

from codemind.agent.tools.source_tools import SourceCodeTools
from codemind.graph.dependency import DependencyGraphService
from codemind.parser.service import CodeParser
from codemind.scanner.service import RepositoryScanner
from codemind.search.hybrid import HybridSearchService
from codemind.search.service import CodeSearchService

SUPPORTED_EXTENSIONS = {".py", ".java"}


class RepositoryTools:
    """Read-only tools for investigating repository code."""

    def __init__(
        self,
        search_service=None,
        hybrid_search_service=None,
        source_tools=None,
        scanner=None,
        parser=None,
        dependency_graph=None,
    ):
        self.search_service = search_service or CodeSearchService()
        self.hybrid_search_service = hybrid_search_service or HybridSearchService()
        self.source_tools = source_tools or SourceCodeTools()
        self.scanner = scanner or RepositoryScanner()
        self.parser = parser or CodeParser()
        self.dependency_graph = dependency_graph or DependencyGraphService()

    def search_symbols(
        self,
        query: str,
        repository_path: str | Path,
    ) -> list[dict]:
        if not query or not query.strip():
            raise ValueError("Symbol search query cannot be empty")

        normalized_path = str(Path(repository_path).expanduser().resolve())

        return self.search_service.search(
            query=query.strip(),
            repository_path=normalized_path,
        )

    def hybrid_search(
        self,
        query: str,
        repository_path: str | Path,
        top_k: int = 5,
    ) -> list[dict]:
        """Search repository code using keyword and semantic retrieval."""

        if not query or not query.strip():
            raise ValueError("Hybrid search query cannot be empty")

        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        normalized_path = str(Path(repository_path).expanduser().resolve())

        return self.hybrid_search_service.search(
            query=query.strip(),
            top_k=top_k,
            repository_path=normalized_path,
        )

    def find_symbol(
        self,
        symbol_name: str,
        repository_path: str | Path,
    ) -> list[dict]:
        if not symbol_name or not symbol_name.strip():
            raise ValueError("Symbol name cannot be empty")

        return self.search_symbols(
            query=symbol_name,
            repository_path=repository_path,
        )

    def get_source(
        self,
        repository_path: str | Path,
        file_path: str,
        start_line: int,
        end_line: int,
    ) -> dict:
        return self.source_tools.get_source(
            repository_path=repository_path,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
        )

    def analyze_change(
        self,
        repository_path: str | Path,
        file_path: str,
    ) -> dict:
        """Find files potentially affected by changing a source file."""

        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty")

        root = Path(repository_path).expanduser().resolve()

        if not root.is_dir():
            raise NotADirectoryError(f"Repository directory does not exist: {root}")

        target = (root / file_path).resolve()

        if not target.is_relative_to(root):
            raise ValueError("Target file is outside the repository")

        if not target.is_file():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        relative_target = target.relative_to(root).as_posix()

        scan_result = self.scanner.scan(root)
        parsed_files = []

        for file_info in scan_result.files:
            if file_info.extension not in SUPPORTED_EXTENSIONS:
                continue

            source_path = root / file_info.path

            try:
                parsed_file = self.parser.parse_file(source_path)
                parsed_file = parsed_file.model_copy(
                    update={"file_path": file_info.path}
                )
                parsed_files.append(parsed_file)

            except (OSError, ValueError):
                continue

        self.dependency_graph.build(parsed_files)

        return self.dependency_graph.analyze_change(relative_target)
