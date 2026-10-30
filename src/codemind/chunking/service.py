from pathlib import Path

from codemind.parser.models import ParsedFile


class CodeChunker:
    """Convert parsed source files into searchable code chunks."""

    def chunk_file(self, file_path: Path, parsed_file: ParsedFile) -> list[dict]:
        """Extract individual code symbols as searchable chunks."""

        source_code = file_path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        lines = source_code.splitlines()
        chunks = []

        for symbol in parsed_file.symbols:
            start = symbol.start_line - 1
            end = symbol.end_line

            code = "\n".join(lines[start:end])

            if not code.strip():
                continue

            chunks.append(
                {
                    "text": code,
                    "metadata": {
                        "file_path": parsed_file.file_path,
                        "symbol": symbol.name,
                        "kind": symbol.kind,
                        "start_line": symbol.start_line,
                        "end_line": symbol.end_line,
                        "language": parsed_file.language,
                    },
                }
            )

        return chunks
