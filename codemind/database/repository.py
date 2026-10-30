from pathlib import Path

from codemind.database.connection import (
    DEFAULT_DB_PATH,
    get_connection,
)
from codemind.parser.models import ParsedFile


class CodeMindRepository:
    """Handle database operations for CodeMind."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path

    def save_repository(self, root_path: str) -> int:
        """Save a repository and return its database ID."""

        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO repositories (root_path)
                VALUES (?)
                ON CONFLICT(root_path) DO NOTHING
                """,
                (root_path,),
            )

            row = connection.execute(
                """
                SELECT id
                FROM repositories
                WHERE root_path = ?
                """,
                (root_path,),
            ).fetchone()

            return row["id"]

    def save_parsed_file(
        self,
        repository_id: int,
        parsed_file: ParsedFile,
    ) -> int:
        """Save parsed file information into SQLite."""

        with get_connection(self.db_path) as connection:
            # Insert or update source file.
            connection.execute(
                """
                INSERT INTO source_files (
                    repository_id,
                    file_path,
                    language
                )
                VALUES (?, ?, ?)
                ON CONFLICT(repository_id, file_path)
                DO UPDATE SET language = excluded.language
                """,
                (
                    repository_id,
                    parsed_file.file_path,
                    parsed_file.language,
                ),
            )

            # Retrieve source file ID.
            row = connection.execute(
                """
                SELECT id
                FROM source_files
                WHERE repository_id = ?
                AND file_path = ?
                """,
                (repository_id, parsed_file.file_path),
            ).fetchone()

            file_id = row["id"]

            # Remove previous extracted records before re-indexing.
            for table in ("symbols", "imports", "calls"):
                connection.execute(
                    f"DELETE FROM {table} WHERE file_id = ?",
                    (file_id,),
                )

            # Save symbols.
            connection.executemany(
                """
                INSERT INTO symbols (
                    file_id,
                    name,
                    kind,
                    start_line,
                    end_line,
                    parameters
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        file_id,
                        symbol.name,
                        symbol.kind,
                        symbol.start_line,
                        symbol.end_line,
                        symbol.parameters,
                    )
                    for symbol in parsed_file.symbols
                ],
            )

            # Save imports.
            connection.executemany(
                """
                INSERT INTO imports (
                    file_id,
                    statement,
                    line
                )
                VALUES (?, ?, ?)
                """,
                [
                    (
                        file_id,
                        item.statement,
                        item.line,
                    )
                    for item in parsed_file.imports
                ],
            )

            # Save function and method calls.
            connection.executemany(
                """
                INSERT INTO calls (
                    file_id,
                    name,
                    line
                )
                VALUES (?, ?, ?)
                """,
                [
                    (
                        file_id,
                        call.name,
                        call.line,
                    )
                    for call in parsed_file.calls
                ],
            )

            return file_id

    def search_symbols(
        self,
        name: str,
        repository_path: str | None = None,
    ) -> list[dict]:
        """Search symbols using partial, case-insensitive matching.

        Optionally restrict results to a specific repository.
        """

        if not name or not name.strip():
            raise ValueError("Symbol search query cannot be empty")

        search_pattern = f"%{name.strip()}%"

        query = """
            SELECT
                symbols.name,
                symbols.kind,
                symbols.start_line,
                symbols.end_line,
                symbols.parameters,
                source_files.file_path,
                source_files.language,
                repositories.root_path
            FROM symbols
            JOIN source_files
                ON symbols.file_id = source_files.id
            JOIN repositories
                ON source_files.repository_id = repositories.id
            WHERE symbols.name LIKE ? COLLATE NOCASE
        """

        parameters = [search_pattern]

        if repository_path is not None:
            query += " AND repositories.root_path = ?"
            parameters.append(repository_path)

        query += """
            ORDER BY
                symbols.name,
                source_files.file_path
        """

        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                query,
                parameters,
            ).fetchall()

            return [dict(row) for row in rows]
