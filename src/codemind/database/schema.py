from pathlib import Path

from codemind.database.connection import (
    DEFAULT_DB_PATH,
    get_connection,
)


SCHEMA = """
CREATE TABLE IF NOT EXISTS repositories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    root_path TEXT NOT NULL UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS source_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    language TEXT NOT NULL,
    FOREIGN KEY (repository_id)
        REFERENCES repositories(id)
        ON DELETE CASCADE,
    UNIQUE(repository_id, file_path)
);

CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    parameters TEXT,
    FOREIGN KEY (file_id)
        REFERENCES source_files(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS imports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    statement TEXT NOT NULL,
    line INTEGER NOT NULL,
    FOREIGN KEY (file_id)
        REFERENCES source_files(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    line INTEGER NOT NULL,
    FOREIGN KEY (file_id)
        REFERENCES source_files(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_symbols_name
ON symbols(name);

CREATE INDEX IF NOT EXISTS idx_symbols_file_id
ON symbols(file_id);

CREATE INDEX IF NOT EXISTS idx_source_files_repository_id
ON source_files(repository_id);
"""


def initialize_database(
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    """Create database tables if they do not exist."""

    with get_connection(db_path) as connection:
        connection.executescript(SCHEMA)
