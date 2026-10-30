from pathlib import Path

from codemind.database.repository import CodeMindRepository


class CodeSearchService:
    """Search indexed code symbols using SQLite."""

    def __init__(self):
        self.database = CodeMindRepository()

    def search(
        self,
        query: str,
        repository_path: str | Path | None = None,
    ) -> list[dict]:
        """Search indexed code symbols, optionally by repository."""

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        normalized_query = query.strip()

        if repository_path is not None:
            normalized_path = str(Path(repository_path).expanduser().resolve())

            return self.database.search_symbols(
                normalized_query,
                repository_path=normalized_path,
            )

        return self.database.search_symbols(normalized_query)
