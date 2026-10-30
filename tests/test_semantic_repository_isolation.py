from codemind.vectorstore.service import VectorStoreService


def test_semantic_search_isolated_by_repository(tmp_path):
    store = VectorStoreService(
        persist_directory=tmp_path,
        collection_name="search_isolation_test",
    )

    embedding = [0.1] * 384

    store.add_code(
        document_id="repo_a_001",
        text="Process ecommerce customer payment",
        embedding=embedding,
        metadata={"repository": "repository_a"},
    )

    store.add_code(
        document_id="repo_b_001",
        text="Process banking customer payment",
        embedding=embedding,
        metadata={"repository": "repository_b"},
    )

    results = store.search(
        query_embedding=embedding,
        top_k=5,
        repository_path="repository_a",
    )

    assert len(results) == 1
    assert results[0]["id"] == "repo_a_001"
    assert results[0]["metadata"]["repository"] == "repository_a"
