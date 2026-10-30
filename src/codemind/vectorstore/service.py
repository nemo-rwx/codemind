import chromadb
from pathlib import Path


class VectorStoreService:
    def get_document_ids(self, repository_path: str) -> list[str]:
        """Get document IDs belonging to one repository."""
        results = self.collection.get(
            where={"repository": repository_path},
            include=["metadatas"],
        )

        return results["ids"]

    def delete_documents(self, document_ids: list[str]) -> None:
        """Delete documents using their IDs."""
        if not document_ids:
            return

        self.collection.delete(ids=document_ids)

    """Manage code embeddings using ChromaDB."""

    def __init__(
        self,
        persist_directory: Path | None = None,
        collection_name: str = "codemind_code",
    ):
        if persist_directory is None:
            persist_directory = Path.home() / ".codemind" / "chroma"

        persist_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client = chromadb.PersistentClient(path=str(persist_directory))

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_code(
        self,
        document_id: str,
        text: str,
        embedding: list[float],
        metadata: dict,
    ) -> None:
        """Store a code document and its embedding."""

        self.collection.upsert(
            ids=[document_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict]:
        """Find code documents similar to the query."""

        if not query_embedding:
            raise ValueError("Query embedding cannot be empty")

        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        matches = []

        for index, document_id in enumerate(results["ids"][0]):
            matches.append(
                {
                    "id": document_id,
                    "text": results["documents"][0][index],
                    "metadata": results["metadatas"][0][index],
                    "distance": results["distances"][0][index],
                }
            )

        return matches

    def count(self) -> int:
        """Return the number of stored documents."""

        return self.collection.count()
