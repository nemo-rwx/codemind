from codemind.vectorstore.service import VectorStoreService


def test_delete_stale_documents(tmp_path):
    store = VectorStoreService(
        persist_directory=tmp_path,
        collection_name="cleanup_test",
    )

    embedding = [0.1] * 384

    # Simulate the first indexing run.
    store.add_code(
        document_id="payment_001",
        text="Process customer payment",
        embedding=embedding,
        metadata={"symbol": "process_payment"},
    )

    store.add_code(
        document_id="report_001",
        text="Generate employee report",
        embedding=embedding,
        metadata={"symbol": "generate_report"},
    )

    assert store.count() == 2

    # Simulate the second indexing run:
    # payment_001 is no longer present in the source code.
    store.delete_documents(["payment_001"])

    assert store.count() == 1

    results = store.search(embedding, top_k=5)

    assert len(results) == 1
    assert results[0]["id"] == "report_001"
