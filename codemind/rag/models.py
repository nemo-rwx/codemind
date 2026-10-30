from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """A code chunk retrieved from the repository."""

    text: str
    file_path: str
    symbol: str
    language: str
    start_line: int
    end_line: int
    score: float | None = None


class RAGContext(BaseModel):
    """Context assembled from retrieved code."""

    query: str
    chunks: list[RetrievedChunk] = Field(default_factory=list)
    total_chunks: int = 0
    context_text: str = ""


class RAGResponse(BaseModel):
    """Final answer generated using retrieved repository context."""

    query: str
    answer: str
    sources: list[RetrievedChunk] = Field(default_factory=list)
