from pathlib import Path


class SourceCodeTools:
    """Safely retrieve source code from a repository."""

    def get_source(
        self,
        repository_path: str | Path,
        file_path: str,
        start_line: int,
        end_line: int,
    ) -> dict:
        if start_line < 1 or end_line < start_line:
            raise ValueError("Invalid source line range")

        root = Path(repository_path).expanduser().resolve()
        source_file = (root / file_path).resolve()

        # Prevent reading files outside the selected repository.
        if not source_file.is_relative_to(root):
            raise ValueError("Source path is outside the repository")

        if not source_file.is_file():
            raise FileNotFoundError(f"Source file not found: {file_path}")

        lines = source_file.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines()

        if start_line > len(lines):
            raise ValueError("Start line exceeds file length")

        actual_end_line = min(end_line, len(lines))

        source = "\n".join(lines[start_line - 1 : actual_end_line])

        return {
            "file_path": file_path,
            "start_line": start_line,
            "end_line": actual_end_line,
            "source_code": source,
        }
