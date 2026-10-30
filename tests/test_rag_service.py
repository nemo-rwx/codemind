import pytest

from codemind.rag.models import RetrievedChunk
from codemind.rag.service import RAGService


class FakeRetriever:
    def retrieve(self, query, repository_path, top_k=5):
        return [
            RetrievedChunk(
                text="def process_payment(amount): return amount",
                file_path="payments.py",
                symbol="process_payment",
                language="python",
                start_line=10,
                end_line=12,
                score=0.05,
            )
        ]


class FakeLLMClient:
    def generate(self, messages):
        assert len(messages) == 2
        return "Payment processing is implemented in process_payment()."


def test_rag_service_ask():
    service = RAGService(
        retriever=FakeRetriever(),
        llm_client=FakeLLMClient(),
    )

    response = service.ask(
        query="How does payment processing work?",
        repository_path=".",
        top_k=3,
    )

    assert response.query == "How does payment processing work?"
    assert "process_payment" in response.answer
    assert len(response.sources) == 1
    assert response.sources[0].file_path == "payments.py"


def test_rag_service_rejects_empty_query():
    service = RAGService(
        retriever=FakeRetriever(),
        llm_client=FakeLLMClient(),
    )

    with pytest.raises(ValueError):
        service.ask(
            query=" ",
            repository_path=".",
        )


def test_rag_service_rejects_invalid_top_k():
    service = RAGService(
        retriever=FakeRetriever(),
        llm_client=FakeLLMClient(),
    )

    with pytest.raises(ValueError):
        service.ask(
            query="Explain payment processing",
            repository_path=".",
            top_k=0,
        )
