from codemind.rag.models import RAGContext, RetrievedChunk


class RAGContextBuilder:
    """Build structured context from retrieved code chunks."""

    def __init__(self, max_context_chars: int = 20000):
        if max_context_chars < 1:
            raise ValueError("max_context_chars must be positive")

        self.max_context_chars = max_context_chars

    def build(
        self,
        query: str,
        chunks: list[RetrievedChunk],
    ) -> RAGContext:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        sections = []
        included_chunks = []
        current_length = 0

        for chunk in chunks:
            section = self._format_chunk(chunk)
            separator = "\n\n" if sections else ""
            required_length = len(separator) + len(section)

            if current_length + required_length > self.max_context_chars:
                break

            sections.append(section)
            included_chunks.append(chunk)
            current_length += required_length

        return RAGContext(
            query=query.strip(),
            chunks=included_chunks,
            total_chunks=len(included_chunks),
            context_text="\n\n".join(sections),
        )

    @staticmethod
    def _format_chunk(chunk: RetrievedChunk) -> str:
        return (
            f"File: {chunk.file_path}\n"
            f"Symbol: {chunk.symbol}\n"
            f"Language: {chunk.language}\n"
            f"Lines: {chunk.start_line}-{chunk.end_line}\n"
            f"Code:\n{chunk.text}"
        )
