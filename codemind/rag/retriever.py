from pathlib import Path

from codemind.rag.models import RetrievedChunk
from codemind.search.hybrid import HybridSearchService


class RAGRetriever:
    """Retrieve relevant code chunks for RAG."""

    def __init__(self, search_service=None):
        self.search_service = search_service or HybridSearchService()

    def retrieve(
        self,
        query: str,
        repository_path: str | Path,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        repository_path = str(Path(repository_path).expanduser().resolve())

        results = self.search_service.search(
            query=query,
            top_k=top_k,
            repository_path=repository_path,
        )

        chunks = []

        for result in results:
            chunks.append(
                RetrievedChunk(
                    text=result.get("text") or "",
                    file_path=result.get("file_path", "Unknown"),
                    symbol=result.get("name", "Unknown"),
                    language=result.get("language", "Unknown"),
                    start_line=result.get("start_line", 0),
                    end_line=result.get("end_line", 0),
                    score=result.get("score"),
                )
            )

        return chunks
