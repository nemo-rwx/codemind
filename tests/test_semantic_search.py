from codemind.search.semantic import SemanticSearchService
from codemind.vectorstore.service import VectorStoreService


def test_semantic_search_integration(tmp_path):
    service = SemanticSearchService()

    # Use an isolated temporary ChromaDB collection.
    service.vector_store = VectorStoreService(
        persist_directory=tmp_path,
        collection_name="test_semantic_search",
    )

    service.index_document(
        document_id="payment_001",
        text="Process customer payment and validate transaction",
        metadata={
            "file_path": "payment.py",
            "symbol": "process_payment",
        },
    )

    results = service.search(
        "How does the application handle payments?",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["id"] == "payment_001"
    assert results[0]["metadata"]["symbol"] == "process_payment"
