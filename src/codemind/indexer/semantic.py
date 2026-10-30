from pathlib import Path

from codemind.chunking.service import CodeChunker
from codemind.embeddings.service import EmbeddingService
from codemind.parser.service import CodeParser
from codemind.scanner.service import RepositoryScanner
from codemind.vectorstore.service import VectorStoreService

SUPPORTED_EXTENSIONS = {".py", ".java"}


class SemanticIndexer:
    """Index repository code into ChromaDB."""

    def __init__(self):
        self.scanner = RepositoryScanner()
        self.parser = CodeParser()
        self.chunker = CodeChunker()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()

    def index_repository(self, root_path: Path) -> dict:
        """Scan, parse, chunk, embed and store repository code."""

        root_path = root_path.expanduser().resolve()

        scan_result = self.scanner.scan(root_path)

        indexed_files = 0
        indexed_chunks = 0
        skipped_files = 0
        failed_files = 0
        errors = []

        current_document_ids = set()

        for file_info in scan_result.files:
            if file_info.extension not in SUPPORTED_EXTENSIONS:
                skipped_files += 1
                continue

            file_path = root_path / file_info.path

            try:
                parsed_file = self.parser.parse_file(file_path)

                chunks = self.chunker.chunk_file(
                    file_path,
                    parsed_file,
                )

                for chunk in chunks:
                    metadata = chunk["metadata"]
                    metadata["repository"] = str(root_path)

                    document_id = (
                        f"{root_path.as_posix()}:"
                        f"{file_info.path}:"
                        f"{metadata['symbol']}:"
                        f"{metadata['start_line']}"
                    )

                    current_document_ids.add(document_id)

                    embedding = self.embedding_service.generate_embedding(chunk["text"])

                    self.vector_store.add_code(
                        document_id=document_id,
                        text=chunk["text"],
                        embedding=embedding,
                        metadata=metadata,
                    )

                    indexed_chunks += 1

                indexed_files += 1

                if parsed_file.errors:
                    errors.extend(
                        f"{file_info.path}: {error}" for error in parsed_file.errors
                    )

            except Exception as error:
                failed_files += 1
                errors.append(f"{file_info.path}: {error}")

        # Remove stale documents only when indexing completed
        # without file-level failures.
        if failed_files == 0:
            previous_document_ids = set(
                self.vector_store.get_document_ids(str(root_path))
            )

            stale_document_ids = list(previous_document_ids - current_document_ids)

            self.vector_store.delete_documents(stale_document_ids)

        return {
            "repository": str(root_path),
            "total_files": scan_result.total_files,
            "indexed_files": indexed_files,
            "skipped_files": skipped_files,
            "failed_files": failed_files,
            "indexed_chunks": indexed_chunks,
            "errors": errors,
        }
