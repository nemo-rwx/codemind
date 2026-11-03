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

    # Debug: print the actual indexing exception.
    print("INDEXING ERRORS:", first_result["errors"])

    assert first_result["failed_files"] == 0

    # Both functions should be indexed.
    assert first_result["total_chunks"] == 2

    # Remove one function from the source file.
    source_file.write_text(
        """
def process_payment(amount):
    return amount * 1.05
""",
        encoding="utf-8",
    )

    # Run indexing again.
    second_result = indexer.index_repository(repository_path)

    print("SECOND INDEXING ERRORS:", second_result["errors"])

    assert second_result["failed_files"] == 0
    assert second_result["total_chunks"] == 1

    # Only the remaining function should exist.
    document_ids = indexer.vector_store.get_document_ids(str(repository_path.resolve()))

    assert len(document_ids) == 1
