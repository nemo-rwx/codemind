import pytest

from codemind.rag.context_builder import RAGContextBuilder
from codemind.rag.models import RetrievedChunk


def create_chunk(symbol, file_path, code):
    return RetrievedChunk(
        text=code,
        file_path=file_path,
        symbol=symbol,
        language="python",
        start_line=1,
        end_line=5,
        score=0.05,
    )


def test_build_context():
    builder = RAGContextBuilder()

    chunks = [
        create_chunk(
            "process_payment",
            "payments.py",
            "def process_payment(): pass",
        ),
        create_chunk(
            "validate_payment",
            "validation.py",
            "def validate_payment(): pass",
        ),
    ]

    context = builder.build(
        query="How does payment processing work?",
        chunks=chunks,
    )

    assert context.total_chunks == 2
    assert "process_payment" in context.context_text
    assert "validate_payment" in context.context_text


def test_context_respects_character_limit():
    builder = RAGContextBuilder(max_context_chars=100)

    chunks = [
        create_chunk(
            "process_payment",
            "payments.py",
            "x" * 200,
        )
    ]

    context = builder.build("payment processing", chunks)

    assert context.total_chunks == 0
    assert context.context_text == ""


def test_rejects_empty_query():
    builder = RAGContextBuilder()

    with pytest.raises(ValueError):
        builder.build("", [])


def test_rejects_invalid_context_limit():
    with pytest.raises(ValueError):
        RAGContextBuilder(max_context_chars=0)
