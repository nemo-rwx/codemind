from pathlib import Path
from typing import ClassVar

from codemind.chunking.service import CodeChunker
from codemind.embeddings.service import EmbeddingService
from codemind.parser.service import CodeParser
from codemind.scanner.service import RepositoryScanner
from codemind.vectorstore.service import VectorStoreService


class SemanticIndexer:
    """Scan, parse, chunk, embed, and index repository source code."""

    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {".py", ".java"}

    def __init__(
        self,
        scanner=None,
        parser=None,
        chunker=None,
        embedding_service=None,
        vector_store=None,
    ):
        self.scanner = scanner or RepositoryScanner()
        self.parser = parser or CodeParser()
        self.chunker = chunker or CodeChunker()
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStoreService()

    def index_repository(self, repository_path: str | Path) -> dict:
        """Create or refresh semantic indexes for a repository."""

        root = Path(repository_path).resolve()

        if not root.exists() or not root.is_dir():
            raise ValueError("Repository path must be an existing directory")

        summary = self.scanner.scan(root)

        indexed_files = 0
        skipped_files = 0
        failed_files = 0
        total_chunks = 0
        errors = []

        repository_id = str(root)

        for file_info in summary.files:
            file_path = Path(file_info.path)

            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                skipped_files += 1
                continue

            absolute_path = root / file_path

            try:
                parsed_file = self.parser.parse_file(absolute_path)

                chunks = self.chunker.chunk_file(
                    parsed_file=parsed_file,
                    source_path=absolute_path,
                )

                if not chunks:
                    indexed_files += 1
                    continue

                texts = [chunk.text for chunk in chunks]

                embeddings = self.embedding_service.generate_embeddings(texts)

                for index, chunk in enumerate(chunks):
                    metadata = {
                        **chunk.metadata,
                        "repository": repository_id,
                        "file_path": str(file_info.path),
                    }

                    document_id = f"{repository_id}:{file_info.path}:{index}"

                    self.vector_store.add_code(
                        document_id=document_id,
                        text=chunk.text,
                        embedding=embeddings[index],
                        metadata=metadata,
                    )

                indexed_files += 1
                total_chunks += len(chunks)

            except Exception as error:  # noqa: BLE001
                # Isolate failures for individual files and continue indexing.
                failed_files += 1
                errors.append(f"{file_info.path}: {error}")

        return {
            "repository_path": repository_id,
            "total_files": summary.total_files,
            "indexed_files": indexed_files,
            "skipped_files": skipped_files,
            "failed_files": failed_files,
            "total_chunks": total_chunks,
            "errors": errors,
        }
