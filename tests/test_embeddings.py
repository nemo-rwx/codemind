from codemind.embeddings.service import EmbeddingService


def test_generate_single_embedding():
    service = EmbeddingService()

    result = service.generate_embedding("Process customer payment")

    assert isinstance(result, list)
    assert len(result) == 384


def test_generate_multiple_embeddings():
    service = EmbeddingService()

    results = service.generate_embeddings(
        [
            "Process customer payment",
            "Generate employee report",
        ]
    )

    assert len(results) == 2
    assert all(len(vector) == 384 for vector in results)


def test_empty_text_raises_error():
    service = EmbeddingService()

    try:
        service.generate_embedding("")
        assert False, "Expected ValueError"
    except ValueError:
        pass
