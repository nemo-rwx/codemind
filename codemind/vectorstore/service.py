from pathlib import Path

import chromadb


class VectorStoreService:
    """Manage code embeddings using persistent ChromaDB storage."""

    def __init__(
        self,
        persist_directory: Path | None = None,
        collection_name: str = "codemind_code",
    ):
        if persist_directory is None:
            persist_directory = Path.home() / ".codemind" / "chroma"

        persist_directory.mkdir(parents=True, exist_ok=True)

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
        """Insert or update a code document and its embedding."""

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
        repository_path: str | None = None,
    ) -> list[dict]:
        """Search for similar code, optionally filtering by repository."""

        if not query_embedding:
            raise ValueError("Query embedding cannot be empty")

        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        total_documents = self.collection.count()

        if total_documents == 0:
            return []

        query_args = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, total_documents),
            "include": [
                "documents",
                "metadatas",
                "distances",
            ],
        }

        if repository_path is not None:
            query_args["where"] = {"repository": repository_path}

        results = self.collection.query(**query_args)

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
        """Return the total number of stored documents."""

        return self.collection.count()

    def get_document_ids(
        self,
        repository_path: str,
    ) -> list[str]:
        """Get document IDs belonging to a specific repository."""

        results = self.collection.get(
            where={"repository": repository_path},
            include=["metadatas"],
        )

        return results["ids"]

    def delete_documents(
        self,
        document_ids: list[str],
    ) -> None:
        """Delete documents using their IDs."""

        if not document_ids:
            return

        self.collection.delete(ids=document_ids)
