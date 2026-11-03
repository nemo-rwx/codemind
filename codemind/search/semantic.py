from pathlib import Path

from codemind.embeddings.service import EmbeddingService
from codemind.vectorstore.service import VectorStoreService


class SemanticSearchService:
    """Search indexed repository code using semantic embeddings."""

    def __init__(
        self,
        embedding_service=None,
        vector_store=None,
    ):
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStoreService()

    def index_document(
        self,
        document_id: str,
        text: str,
        metadata: dict,
    ) -> None:
        """Generate an embedding and index a single document."""

        if not document_id or not document_id.strip():
            raise ValueError("Document ID cannot be empty")

        if not text or not text.strip():
            raise ValueError("Document text cannot be empty")

        if not isinstance(metadata, dict):
            raise ValueError("Metadata must be a dictionary")  # noqa: TRY004

        embedding = self.embedding_service.generate_embedding(text)

        self.vector_store.add_code(
            document_id=document_id,
            text=text,
            embedding=embedding,
            metadata=metadata,
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        repository_path: str | Path | None = None,
    ) -> list[dict]:
        """Return semantically similar code chunks."""

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Search query cannot be empty")

        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
            raise ValueError("top_k must be a positive integer")

        query_embedding = self.embedding_service.generate_query_embedding(query.strip())

        normalized_path = None

        if repository_path is not None:
            normalized_path = str(Path(repository_path).expanduser().resolve())

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            repository_path=normalized_path,
        )

        return results or []

    def count(self) -> int:
        """Return the number of indexed documents."""

        return self.vector_store.count()
