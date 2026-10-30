from pathlib import Path

from codemind.database.repository import CodeMindRepository


class CodeSearchService:
    def __init__(self):
        self.database = CodeMindRepository()

    def search(self, query: str) -> list[dict]:
        """Search indexed code symbols."""

        if not query.strip():
            raise ValueError("Search query cannot be empty")

        return self.database.search_symbols(query.strip())
