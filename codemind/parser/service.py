from pathlib import Path

import tree_sitter_java as tsjava
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

from codemind.parser.models import (
    CodeCall,
    CodeImport,
    CodeSymbol,
    ParsedFile,
)


class CodeParser:
    def __init__(self):
        self.parsers = {
            ".py": (
                "Python",
                Parser(Language(tspython.language())),
            ),
            ".java": (
                "Java",
                Parser(Language(tsjava.language())),
            ),
        }

    def parse_file(self, file_path: Path) -> ParsedFile:
        """Parse a Python or Java file and extract code structures."""

        file_path = file_path.expanduser().resolve()
        extension = file_path.suffix.lower()

        if extension not in self.parsers:
            raise ValueError(f"Unsupported language: {extension}")

        language, parser = self.parsers[extension]
        source_code = file_path.read_bytes()

        tree = parser.parse(source_code)

        result = ParsedFile(
            file_path=str(file_path),
            language=language,
        )

        self._extract_nodes(
            tree.root_node,
            source_code,
            result,
            language,
        )

        if tree.root_node.has_error:
            result.errors.append("The syntax tree contains parsing errors.")

        return result

    def _extract_nodes(
        self,
        node,
        source_code: bytes,
        result: ParsedFile,
        language: str,
    ) -> None:
        """Traverse the syntax tree and extract useful nodes."""

        symbol_types = {
            "class_definition": "class",
            "function_definition": "function",
            "class_declaration": "class",
            "interface_declaration": "interface",
            "enum_declaration": "enum",
            "method_declaration": "method",
            "constructor_declaration": "constructor",
        }

        import_types = {
            "import_statement",
            "import_from_statement",
            "import_declaration",
        }

        for node_type, kind in symbol_types.items():
            if node.type == node_type:
                name_node = node.child_by_field_name("name")

                if name_node is not None:
                    parameters_node = node.child_by_field_name("parameters")

                    parameters = (
                        parameters_node.text.decode("utf-8")
                        if parameters_node is not None
                        else None
                    )

                    result.symbols.append(
                        CodeSymbol(
                            name=name_node.text.decode("utf-8"),
                            kind=kind,
                            start_line=node.start_point.row + 1,
                            end_line=node.end_point.row + 1,
                            parameters=parameters,
                        )
                    )
                break

        if node.type in import_types:
            result.imports.append(
                CodeImport(
                    statement=node.text.decode("utf-8"),
                    line=node.start_point.row + 1,
                )
            )

        if language == "Python" and node.type == "call":
            function_node = node.child_by_field_name("function")

            if function_node is not None:
                result.calls.append(
                    CodeCall(
                        name=function_node.text.decode("utf-8"),
                        line=node.start_point.row + 1,
                    )
                )

        if language == "Java" and node.type == "method_invocation":
            name_node = node.child_by_field_name("name")

            if name_node is not None:
                result.calls.append(
                    CodeCall(
                        name=name_node.text.decode("utf-8"),
                        line=node.start_point.row + 1,
                    )
                )

        for child in node.children:
            self._extract_nodes(
                child,
                source_code,
                result,
                language,
            )
