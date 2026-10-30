import pytest

from codemind.rag.models import RAGContext, RetrievedChunk
from codemind.rag.prompt_builder import RAGPromptBuilder


def create_context():
    chunk = RetrievedChunk(
        text="def process_payment(amount): return amount",
        file_path="payments.py",
        symbol="process_payment",
        language="python",
        start_line=10,
        end_line=12,
        score=0.05,
    )

    return RAGContext(
        query="How does payment processing work?",
        chunks=[chunk],
        total_chunks=1,
        context_text=(
            "File: payments.py\n"
            "Symbol: process_payment\n"
            "Lines: 10-12\n"
            "Code:\n"
            "def process_payment(amount): return amount"
        ),
    )


def test_build_messages():
    builder = RAGPromptBuilder()

    messages = builder.build_messages(create_context())

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_prompt_contains_developer_question():
    builder = RAGPromptBuilder()

    messages = builder.build_messages(create_context())

    assert "How does payment processing work?" in messages[1]["content"]


def test_prompt_contains_repository_context():
    builder = RAGPromptBuilder()

    messages = builder.build_messages(create_context())

    assert "payments.py" in messages[1]["content"]
    assert "process_payment" in messages[1]["content"]


def test_prompt_handles_empty_context():
    builder = RAGPromptBuilder()

    context = RAGContext(
        query="Explain payment processing",
        chunks=[],
        total_chunks=0,
        context_text="",
    )

    messages = builder.build_messages(context)

    assert "No relevant repository code was retrieved." in (messages[1]["content"])


def test_rejects_empty_query():
    builder = RAGPromptBuilder()

    context = RAGContext(
        query=" ",
        chunks=[],
        total_chunks=0,
        context_text="",
    )

    with pytest.raises(ValueError):
        builder.build_messages(context)
