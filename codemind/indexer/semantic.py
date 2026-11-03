from pathlib import Path
from typing import ClassVar

from codemind.chunking.service import CodeChunker
from codemind.embeddings.service import EmbeddingService
from codemind.parser.service import CodeParser
from codemind.scanner.service import RepositoryScanner
from codemind.vectorstore.service import VectorStoreService


class SemanticIndexer:
    """Build and maintain a semantic index for a code repository."""

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
        """Scan, parse, chunk, and index a repository."""

        root_path = Path(repository_path).expanduser().resolve()

        if not root_path.exists():
            raise FileNotFoundError(f"Repository not found: {root_path}")

        if not root_path.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {root_path}")

        repository_id = str(root_path)

        existing_ids = set(self.vector_store.get_document_ids(repository_id))

        current_ids = set()
        indexed_files = 0
        failed_files = 0
        skipped_files = 0
        total_chunks = 0
        errors = []

        summary = self.scanner.scan(root_path)

        for file_info in summary.files:
            relative_path = Path(file_info.path)

            if relative_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                skipped_files += 1
                continue

            absolute_path = root_path / relative_path

            try:
                parsed_file = self.parser.parse_file(absolute_path)

                chunks = self.chunker.chunk_file(
                    file_path=absolute_path,
                    parsed_file=parsed_file,
                )

                texts = [chunk["text"] for chunk in chunks]

                if texts:
                    embeddings = self.embedding_service.generate_embeddings(texts)

                    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                        metadata = {
                            **chunk["metadata"],
                            "repository": repository_id,
                            "file_path": relative_path.as_posix(),
                        }

                        document_id = (
                            f"{repository_id}:"
                            f"{relative_path.as_posix()}:"
                            f"{metadata['symbol']}:"
                            f"{index}"
                        )

                        self.vector_store.add_code(
                            document_id=document_id,
                            text=chunk["text"],
                            embedding=embedding,
                            metadata=metadata,
                        )

                        current_ids.add(document_id)
                        total_chunks += 1

                indexed_files += 1

            except Exception as error:  # noqa: BLE001
                failed_files += 1
                errors.append(f"{file_info.path}: {error}")

        # Preserve existing data if any file failed to index.
        if failed_files == 0 and not summary.errors:
            stale_ids = existing_ids - current_ids

            if stale_ids:
                self.vector_store.delete_documents(list(stale_ids))

        return {
            "repository": repository_id,
            "total_files": summary.total_files,
            "indexed_files": indexed_files,
            "skipped_files": skipped_files,
            "failed_files": failed_files,
            "indexed_chunks": total_chunks,
            "total_chunks": total_chunks,
            "errors": errors,
        }
