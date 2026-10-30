from codemind.vectorstore.service import VectorStoreService


def test_repository_cleanup_does_not_delete_other_repositories(tmp_path):
    store = VectorStoreService(
        persist_directory=tmp_path,
        collection_name="repository_isolation_test",
    )

    embedding = [0.1] * 384

    store.add_code(
        document_id="repo_a_001",
        text="Repository A payment function",
        embedding=embedding,
        metadata={"repository": "repository_a"},
    )

    store.add_code(
        document_id="repo_b_001",
        text="Repository B reporting function",
        embedding=embedding,
        metadata={"repository": "repository_b"},
    )

    assert store.count() == 2

    # Repository A no longer contains its indexed document.
    repo_a_documents = store.get_document_ids("repository_a")

    store.delete_documents(repo_a_documents)

    assert store.get_document_ids("repository_a") == []
    assert store.get_document_ids("repository_b") == ["repo_b_001"]
    assert store.count() == 1
