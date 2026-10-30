import chromadb

from codemind.vectorstore.service import VectorStoreService


def test_chromadb_persistence_across_clients(tmp_path):
    database_path = tmp_path / "chroma_test"

    embedding = [0.1] * 384

    # First client: create collection and store document.
    first_store = VectorStoreService(
        persist_directory=database_path,
        collection_name="persistence_test",
    )

    first_store.add_code(
        document_id="payment_001",
        text="Process customer payment",
        embedding=embedding,
        metadata={
            "file_path": "payment.py",
            "symbol": "process_payment",
        },
    )

    assert first_store.count() == 1

    # Close the first ChromaDB client.
    first_store.client = None
    first_store.collection = None

    # Second client: reopen the same database directory.
    second_client = chromadb.PersistentClient(path=str(database_path))

    second_collection = second_client.get_collection(name="persistence_test")

    # Verify that the original document still exists.
    assert second_collection.count() == 1

    results = second_collection.query(
        query_embeddings=[embedding],
        n_results=1,
        include=["documents", "metadatas"],
    )

    assert results["ids"][0][0] == "payment_001"
    assert results["documents"][0][0] == "Process customer payment"
    assert results["metadatas"][0][0]["symbol"] == "process_payment"
