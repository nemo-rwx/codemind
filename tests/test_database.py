from pathlib import Path

from codemind.database.repository import CodeMindRepository
from codemind.database.schema import initialize_database
from codemind.parser.models import (
    CodeCall,
    CodeImport,
    CodeSymbol,
    ParsedFile,
)


def test_save_and_search_code_symbols(tmp_path: Path):
    db_path = tmp_path / "test_codemind.db"

    # 1. Initialize database
    initialize_database(db_path)

    # 2. Create database repository
    database = CodeMindRepository(db_path)

    # 3. Save repository
    repository_id = database.save_repository("C:/projects/payment-service")

    # 4. Create parsed file data
    parsed_file = ParsedFile(
        file_path="C:/projects/payment-service/PaymentService.java",
        language="Java",
        symbols=[
            CodeSymbol(
                name="PaymentService",
                kind="class",
                start_line=1,
                end_line=10,
            ),
            CodeSymbol(
                name="processPayment",
                kind="method",
                start_line=3,
                end_line=8,
                parameters="(double amount)",
            ),
        ],
        imports=[
            CodeImport(
                statement="import java.util.List;",
                line=1,
            )
        ],
        calls=[
            CodeCall(
                name="save",
                line=5,
            )
        ],
    )

    # 5. Save parsed information
    database.save_parsed_file(repository_id, parsed_file)

    # 6. Search for a symbol
    results = database.search_symbols("processPayment")

    assert len(results) == 1
    assert results[0]["name"] == "processPayment"
    assert results[0]["kind"] == "method"
    assert results[0]["language"] == "Java"
