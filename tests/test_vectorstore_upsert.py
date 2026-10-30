from codemind.vectorstore.service import VectorStoreService


def test_upsert_updates_existing_document(tmp_path):
    store = VectorStoreService(
        persist_directory=tmp_path,
        collection_name="upsert_test",
    )

    embedding = [0.1] * 384

    store.add_code(
        document_id="payment_001",
        text="Original payment implementation",
        embedding=embedding,
        metadata={"symbol": "process_payment"},
    )

    assert store.count() == 1

    # Index the same document ID again with updated content.
    store.add_code(
        document_id="payment_001",
        text="Updated payment implementation",
        embedding=embedding,
        metadata={"symbol": "process_payment"},
    )

    # The second operation should update, not duplicate.
    assert store.count() == 1

    results = store.search(embedding, top_k=1)

    assert len(results) == 1
    assert results[0]["text"] == "Updated payment implementation"
