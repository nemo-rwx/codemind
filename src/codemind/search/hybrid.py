from codemind.search.service import CodeSearchService
from codemind.search.semantic import SemanticSearchService


class HybridSearchService:
    """Combine keyword and semantic search using RRF."""

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
    ) -> list[dict]:
        """Perform hybrid search and combine ranked results."""

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        query = query.strip()

        keyword_results = self.keyword_search.search(query)

        semantic_results = self.semantic_search.search(
            query,
            top_k=top_k * 2,
        )

        combined = {}
        rrf_constant = 60

        # Process keyword search results.
        for rank, result in enumerate(keyword_results, start=1):
            key = (
                result["file_path"],
                result["name"],
                result["start_line"],
            )

            if key not in combined:
                combined[key] = {
                    "name": result["name"],
                    "kind": result["kind"],
                    "file_path": result["file_path"],
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

        # Process semantic search results.
        for rank, result in enumerate(semantic_results, start=1):
            metadata = result["metadata"]

            name = metadata.get("symbol", "Unknown")
            file_path = metadata.get("file_path", "Unknown")
            start_line = metadata.get("start_line", 0)

            key = (file_path, name, start_line)

            if key not in combined:
                combined[key] = {
                    "name": name,
                    "kind": metadata.get("kind", "Unknown"),
                    "file_path": file_path,
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
