from codemind.indexer.semantic import SemanticIndexer
from codemind.vectorstore.service import VectorStoreService


def test_semantic_indexer_removes_deleted_functions(tmp_path):
    repository_path = tmp_path / "sample_repo"
    repository_path.mkdir()

    source_file = repository_path / "payments.py"

    source_file.write_text(
        """
def process_payment(amount):
    return amount * 1.05


def generate_invoice(amount):
    return f"Invoice: {amount}"
""",
        encoding="utf-8",
    )

    # Use an isolated ChromaDB collection.
    indexer = SemanticIndexer()
    indexer.vector_store = VectorStoreService(
        persist_directory=tmp_path / "chroma",
        collection_name="indexer_cleanup_test",
    )

    # First indexing run.
    first_result = indexer.index_repository(repository_path)

    assert first_result["failed_files"] == 0
    assert first_result["indexed_chunks"] == 2
    assert indexer.vector_store.count() == 2

    # Delete one function from the source file.
    source_file.write_text(
        """
def generate_invoice(amount):
    return f"Invoice: {amount}"
""",
        encoding="utf-8",
    )

    # Second indexing run.
    second_result = indexer.index_repository(repository_path)

    assert second_result["failed_files"] == 0
    assert second_result["indexed_chunks"] == 1
    assert indexer.vector_store.count() == 1

    remaining_ids = indexer.vector_store.get_document_ids(
        str(repository_path.resolve())
    )

    assert len(remaining_ids) == 1
    assert "generate_invoice" in remaining_ids[0]
