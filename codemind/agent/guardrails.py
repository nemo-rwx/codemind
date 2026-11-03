import json
from pathlib import Path
from typing import ClassVar


class GuardrailError(ValueError):
    """Raised when an agent tool request violates security rules."""


class GuardrailService:
    """Validate agent tool calls before execution."""

    ALLOWED_TOOLS: ClassVar[set[str]] = {
        "hybrid_search",
        "search_symbols",
        "find_symbol",
        "get_source",
        "analyze_change",
    }

    MAX_TOOL_INPUT_LENGTH = 2000
    MAX_SOURCE_LINES = 500

    def validate_tool_call(
        self,
        tool_name: str,
        tool_input: str,
        repository_path: str,
    ) -> dict:
        """Validate a tool call and return normalized arguments."""

        if tool_name not in self.ALLOWED_TOOLS:
            raise GuardrailError(f"Tool not allowed: {tool_name}")

        if not isinstance(tool_input, str):
            raise TypeError("Tool input must be a string")

        if len(tool_input) > self.MAX_TOOL_INPUT_LENGTH:
            raise GuardrailError("Tool input is too long")

        root = Path(repository_path).resolve()

        if not root.exists() or not root.is_dir():
            raise GuardrailError("Repository path must be an existing directory")

        if tool_name in {
            "hybrid_search",
            "search_symbols",
            "find_symbol",
        }:
            if not tool_input.strip():
                raise GuardrailError("Search input cannot be empty")

            return {"query": tool_input.strip()}

        if tool_name == "analyze_change":
            file_path = self._validate_repository_file(root, tool_input)
            return {"file_path": file_path}

        if tool_name == "get_source":
            try:
                arguments = json.loads(tool_input)
            except json.JSONDecodeError as error:
                raise GuardrailError("Source arguments must be valid JSON") from error

            if not isinstance(arguments, dict):
                raise GuardrailError("Source arguments must be a JSON object")

            expected_keys = {
                "file_path",
                "start_line",
                "end_line",
            }

            if set(arguments) != expected_keys:
                raise GuardrailError(
                    "Source arguments must contain file_path, start_line, and end_line"
                )

            file_path = arguments["file_path"]
            start_line = arguments["start_line"]
            end_line = arguments["end_line"]

            if not isinstance(file_path, str):
                raise TypeError("file_path must be a string")

            if (
                not isinstance(start_line, int)
                or isinstance(start_line, bool)
                or not isinstance(end_line, int)
                or isinstance(end_line, bool)
            ):
                raise TypeError("Line numbers must be integers")

            if start_line < 1 or end_line < start_line:
                raise GuardrailError("Invalid source line range")

            if end_line - start_line + 1 > self.MAX_SOURCE_LINES:
                raise GuardrailError("Requested source range is too large")

            normalized_path = self._validate_repository_file(root, file_path)

            return {
                "file_path": normalized_path,
                "start_line": start_line,
                "end_line": end_line,
            }

        raise GuardrailError("Unsupported tool")

    @staticmethod
    def _validate_repository_file(
        root: Path,
        file_path: str,
    ) -> str:
        """Ensure a file is inside the repository and exists."""

        if not file_path or not file_path.strip():
            raise GuardrailError("File path cannot be empty")

        candidate = Path(file_path)

        if candidate.is_absolute():
            raise GuardrailError("Absolute paths are not allowed")

        resolved = (root / candidate).resolve()

        try:
            relative_path = resolved.relative_to(root)
        except ValueError as error:
            raise GuardrailError("File path escapes the repository") from error

        if not resolved.is_file():
            raise GuardrailError("Requested repository file does not exist")

        return relative_path.as_posix()
