from pathlib import Path

from codemind.database.repository import CodeMindRepository
from codemind.database.schema import initialize_database
from codemind.parser.service import CodeParser
from codemind.scanner.service import RepositoryScanner

SUPPORTED_EXTENSIONS = {".py", ".java"}


class RepositoryIndexer:
    def __init__(self):
        self.scanner = RepositoryScanner()
        self.parser = CodeParser()
        self.database = CodeMindRepository()

    def index_repository(self, root_path: Path) -> dict:
        """Scan, parse, and store a repository."""

        root_path = root_path.expanduser().resolve()

        # Step 1: Initialize the database.
        initialize_database(self.database.db_path)

        # Step 2: Scan the repository.
        scan_result = self.scanner.scan(root_path)

        # Step 3: Register the repository.
        repository_id = self.database.save_repository(str(root_path))

        indexed_files = 0
        skipped_files = 0
        failed_files = 0

        total_symbols = 0
        total_imports = 0
        total_calls = 0

        errors = []

        # Step 4: Process each discovered file.
        for file_info in scan_result.files:
            # Only parse Python and Java files for now.
            if file_info.extension not in SUPPORTED_EXTENSIONS:
                skipped_files += 1
                continue

            file_path = root_path / file_info.path

            try:
                # Parse source code.
                parsed_file = self.parser.parse_file(file_path)

                # Save extracted information.
                self.database.save_parsed_file(
                    repository_id,
                    parsed_file,
                )

                indexed_files += 1

                total_symbols += len(parsed_file.symbols)
                total_imports += len(parsed_file.imports)
                total_calls += len(parsed_file.calls)

                if parsed_file.errors:
                    errors.extend(
                        f"{file_info.path}: {error}" for error in parsed_file.errors
                    )

            except Exception as error:
                failed_files += 1
                errors.append(f"{file_info.path}: {error}")

        # Step 5: Return indexing statistics.
        return {
            "repository": str(root_path),
            "total_files": scan_result.total_files,
            "indexed_files": indexed_files,
            "skipped_files": skipped_files,
            "failed_files": failed_files,
            "total_symbols": total_symbols,
            "total_imports": total_imports,
            "total_calls": total_calls,
            "errors": errors,
        }
