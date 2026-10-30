from sentence_transformers import SentenceTransformer


class EmbeddingService:
    MODEL_NAME = "BAAI/bge-small-en-v1.5"

    QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

    def __init__(self):
        self.model = SentenceTransformer(self.MODEL_NAME)

    def generate_embedding(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        embedding = self.model.encode(
            text.strip(),
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def generate_query_embedding(self, query: str) -> list[float]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        formatted_query = self.QUERY_PREFIX + query.strip()

        embedding = self.model.encode(
            formatted_query,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        if any(not text or not text.strip() for text in texts):
            raise ValueError("Texts cannot contain empty values")

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return embeddings.tolist()
