from codemind.vectorstore.service import VectorStoreService


def test_deleted_document_remains_without_cleanup(tmp_path):
    store = VectorStoreService(
        persist_directory=tmp_path,
        collection_name="stale_test",
    )

    embedding = [0.1] * 384

    # First indexing run.
    store.add_code(
        document_id="payment_001",
        text="Process customer payment",
        embedding=embedding,
        metadata={"symbol": "process_payment"},
    )

    # Second indexing run: function is deleted.
    # No new document is added, but no cleanup happens either.

    assert store.count() == 1

    results = store.search(embedding, top_k=1)

    # The deleted function is still searchable!
    assert results[0]["metadata"]["symbol"] == "process_payment"
