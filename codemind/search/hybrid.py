from pathlib import Path

from codemind.search.semantic import SemanticSearchService
from codemind.search.service import CodeSearchService


class HybridSearchService:
    """Combine keyword and semantic search using Reciprocal Rank Fusion."""

    def __init__(
        self,
        keyword_search=None,
        semantic_search=None,
    ):
        self.keyword_search = keyword_search or CodeSearchService()
        self.semantic_search = semantic_search or SemanticSearchService()

    def search(
        self,
        query: str,
        top_k: int = 5,
        repository_path: str | Path | None = None,
    ) -> list[dict]:
        """Search using keyword and semantic retrieval."""

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        query = query.strip()

        normalized_path = None

        if repository_path is not None:
            normalized_path = str(Path(repository_path).expanduser().resolve())

        # Retrieve keyword results.
        if normalized_path is None:
            keyword_results = self.keyword_search.search(query)
        else:
            keyword_results = self.keyword_search.search(
                query,
                repository_path=normalized_path,
            )

        # Retrieve semantic results.
        if normalized_path is None:
            semantic_results = self.semantic_search.search(
                query,
                top_k=top_k * 2,
            )
        else:
            semantic_results = self.semantic_search.search(
                query,
                top_k=top_k * 2,
                repository_path=normalized_path,
            )

        combined = {}
        rrf_constant = 60

        # Process keyword results.
        for rank, result in enumerate(keyword_results, start=1):
            repository = result.get("root_path")

            key = (
                repository,
                result["file_path"],
                result["name"],
                result["start_line"],
            )

            if key not in combined:
                combined[key] = {
                    "name": result["name"],
                    "kind": result["kind"],
                    "file_path": result["file_path"],
                    "repository": repository,
                    "language": result["language"],
                    "start_line": result["start_line"],
                    "end_line": result["end_line"],
                    "parameters": result.get("parameters"),
                    "text": None,
                    "distance": None,
                    "sources": [],
                    "score": 0.0,
                }

            combined[key]["score"] += 1 / (rrf_constant + rank)
            combined[key]["sources"].append("keyword")

        # Process semantic results.
        for rank, result in enumerate(semantic_results, start=1):
            metadata = result["metadata"]

            name = metadata.get("symbol", "Unknown")
            file_path = metadata.get("file_path", "Unknown")
            start_line = metadata.get("start_line", 0)
            repository = metadata.get("repository")

            key = (
                repository,
                file_path,
                name,
                start_line,
            )

            if key not in combined:
                combined[key] = {
                    "name": name,
                    "kind": metadata.get("kind", "Unknown"),
                    "file_path": file_path,
                    "repository": repository,
                    "language": metadata.get("language", "Unknown"),
                    "start_line": start_line,
                    "end_line": metadata.get("end_line", 0),
                    "parameters": None,
                    "text": result["text"],
                    "distance": result["distance"],
                    "sources": [],
                    "score": 0.0,
                }
            else:
                combined[key]["text"] = result["text"]
                combined[key]["distance"] = result["distance"]

            combined[key]["score"] += 1 / (rrf_constant + rank)

            if "semantic" not in combined[key]["sources"]:
                combined[key]["sources"].append("semantic")

        ranked_results = sorted(
            combined.values(),
            key=lambda item: item["score"],
            reverse=True,
        )

        return ranked_results[:top_k]
