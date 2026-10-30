import pytest

from codemind.rag.retriever import RAGRetriever


class FakeHybridSearch:
    def search(self, query, top_k=5, repository_path=None):
        return [
            {
                "name": "process_payment",
                "file_path": "payments.py",
                "language": "python",
                "start_line": 10,
                "end_line": 20,
                "text": "def process_payment(amount): return amount",
                "score": 0.04,
            }
        ]


def test_retrieve_code_chunks():
    retriever = RAGRetriever(search_service=FakeHybridSearch())

    results = retriever.retrieve(
        query="How does payment processing work?",
        repository_path=".",
        top_k=5,
    )

    assert len(results) == 1
    assert results[0].symbol == "process_payment"
    assert results[0].file_path == "payments.py"
    assert results[0].language == "python"
    assert results[0].start_line == 10


def test_rejects_empty_query():
    retriever = RAGRetriever(search_service=FakeHybridSearch())

    with pytest.raises(ValueError):
        retriever.retrieve(
            query=" ",
            repository_path=".",
        )


def test_rejects_invalid_top_k():
    retriever = RAGRetriever(search_service=FakeHybridSearch())

    with pytest.raises(ValueError):
        retriever.retrieve(
            query="payment",
            repository_path=".",
            top_k=0,
        )
