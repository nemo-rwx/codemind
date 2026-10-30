from codemind.vectorstore.service import VectorStoreService


def test_add_and_search_code(tmp_path):
    store = VectorStoreService(persist_directory=tmp_path)

    embedding = [0.1] * 384

    store.add_code(
        document_id="payment_service",
        text="Process customer payment",
        embedding=embedding,
        metadata={
            "file_path": "payment.py",
            "symbol": "process_payment",
        },
    )

    assert store.count() == 1

    results = store.search(
        query_embedding=embedding,
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["id"] == "payment_service"
    assert results[0]["metadata"]["symbol"] == "process_payment"


def test_empty_query_embedding_raises_error(tmp_path):
    store = VectorStoreService(persist_directory=tmp_path)

    try:
        store.search([])
        assert False, "Expected ValueError"
    except ValueError:
        pass
