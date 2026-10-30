from pathlib import Path

from codemind.chunking.service import CodeChunker
from codemind.parser.models import CodeSymbol, ParsedFile


def test_chunk_file(tmp_path):
    source = """class PaymentService:
    def process_payment(self):
        print("Processing payment")
"""

    file_path = tmp_path / "payment.py"
    file_path.write_text(source, encoding="utf-8")

    parsed_file = ParsedFile(
        file_path="payment.py",
        language="Python",
        symbols=[
            CodeSymbol(
                name="PaymentService",
                kind="class",
                start_line=1,
                end_line=3,
            ),
            CodeSymbol(
                name="process_payment",
                kind="function",
                start_line=2,
                end_line=3,
                parameters="self",
            ),
        ],
    )

    chunker = CodeChunker()
    chunks = chunker.chunk_file(file_path, parsed_file)

    assert len(chunks) == 2
    assert chunks[0]["metadata"]["symbol"] == "PaymentService"
    assert chunks[1]["metadata"]["symbol"] == "process_payment"
    assert "Processing payment" in chunks[1]["text"]
