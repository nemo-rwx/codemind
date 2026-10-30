from codemind.embeddings.service import EmbeddingService
from codemind.vectorstore.service import VectorStoreService


class SemanticSearchService:
    """Perform semantic search over indexed code."""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()

    def index_document(
        self,
        document_id: str,
        text: str,
        metadata: dict,
    ) -> None:
        """Generate an embedding and store a code document."""

        if not document_id or not document_id.strip():
            raise ValueError("Document ID cannot be empty")

        if not text or not text.strip():
            raise ValueError("Document text cannot be empty")

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
        repository_path: str | None = None,
    ) -> list[dict]:
        """Search code using natural-language queries."""

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        if self.vector_store.count() == 0:
            return []

        query_embedding = self.embedding_service.generate_query_embedding(query)

        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            repository_path=repository_path,
        )
