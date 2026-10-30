from pathlib import Path

from codemind.llm.openrouter import OpenRouterClient
from codemind.rag.context_builder import RAGContextBuilder
from codemind.rag.models import RAGResponse
from codemind.rag.prompt_builder import RAGPromptBuilder
from codemind.rag.retriever import RAGRetriever


class RAGService:
    """Coordinate retrieval, context construction, and LLM generation."""

    def __init__(
        self,
        retriever: RAGRetriever | None = None,
        context_builder: RAGContextBuilder | None = None,
        prompt_builder: RAGPromptBuilder | None = None,
        llm_client: OpenRouterClient | None = None,
    ):
        self.retriever = retriever or RAGRetriever()
        self.context_builder = context_builder or RAGContextBuilder()
        self.prompt_builder = prompt_builder or RAGPromptBuilder()
        self.llm_client = llm_client or OpenRouterClient()

    def ask(
        self,
        query: str,
        repository_path: str | Path,
        top_k: int = 5,
    ) -> RAGResponse:
        """Answer a question using retrieved repository context."""

        if not isinstance(query, str):
            raise TypeError("Query must be a string")

        if not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        repository = Path(repository_path).resolve()

        if not repository.exists() or not repository.is_dir():
            raise ValueError("Repository path must be an existing directory")

        chunks = self.retriever.retrieve(
            query=query.strip(),
            repository_path=repository,
            top_k=top_k,
        )

        context = self.context_builder.build(
            query=query.strip(),
            chunks=chunks,
        )

        messages = self.prompt_builder.build_messages(context)

        answer = self.llm_client.generate(messages)

        return RAGResponse(
            query=query.strip(),
            answer=answer,
            sources=context.chunks,
        )
