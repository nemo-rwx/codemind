from pathlib import Path

import networkx as nx

from codemind.parser.models import ParsedFile


class DependencyGraphService:
    """Build and query a directed source-file dependency graph."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def analyze_change(self, file_path: str) -> dict:
        """Identify files potentially affected by a change."""

        normalized_path = self._normalize_path(file_path)

        if normalized_path not in self.graph:
            return {
                "file_path": normalized_path,
                "exists": False,
                "direct_dependents": [],
                "affected_files": [],
                "total_affected": 0,
            }

        direct_dependents = self.get_dependents(normalized_path)
        affected_files = self.get_impact(normalized_path)

        return {
            "file_path": normalized_path,
            "exists": True,
            "direct_dependents": direct_dependents,
            "affected_files": sorted(affected_files),
            "total_affected": len(affected_files),
        }

    def build(self, parsed_files: list[ParsedFile]) -> nx.DiGraph:
        """Build a dependency graph from parsed repository files."""

        self.graph.clear()

        # Register every parsed file as a graph node.
        for parsed_file in parsed_files:
            file_path = self._normalize_path(parsed_file.file_path)

            self.graph.add_node(
                file_path,
                language=parsed_file.language,
            )

        # Resolve imports that match files in the parsed repository.
        known_files = set(self.graph.nodes)

        for parsed_file in parsed_files:
            source_file = self._normalize_path(parsed_file.file_path)

            for imported in parsed_file.imports:
                target_file = self._resolve_import(
                    source_file,
                    imported.statement,
                    known_files,
                )

                if target_file is not None:
                    self.graph.add_edge(
                        source_file,
                        target_file,
                    )

        return self.graph

    @staticmethod
    def _normalize_path(file_path: str) -> str:
        return Path(file_path).as_posix()

    def _resolve_import(
        self,
        source_file: str,
        import_statement: str,
        known_files: set[str],
    ) -> str | None:
        """Resolve a basic Python or Java import to a parsed file."""

        statement = import_statement.strip()

        if not statement:
            return None

        # Python: import package.module
        # Python: from package.module import Class
        if statement.startswith("from "):
            module = statement[5:].split(" import ")[0].strip()
        elif statement.startswith("import "):
            module = statement[7:].split(" as ")[0].strip()
        else:
            # Java: import com.example.PaymentService;
            if not statement.startswith("import "):
                return None

            module = statement[7:].strip().rstrip(";")
            module = module.removesuffix(".*")

        module_path = module.replace(".", "/")

        candidates = [
            f"{module_path}.py",
            f"{module_path}.java",
        ]

        # Also support Java imports where the class name is
        # the filename and the package path is not fully known.
        for candidate in candidates:
            for known_file in known_files:
                if known_file.endswith(candidate):
                    return known_file

        # Python relative imports are handled conservatively.
        if statement.startswith("from ."):
            parent = Path(source_file).parent
            relative_module = statement[5:].split(" import ")[0]
            candidate = (
                parent / (relative_module.replace(".", "/") + ".py")
            ).as_posix()

            if candidate in known_files:
                return candidate

        return None

    def get_dependencies(self, file_path: str) -> list[str]:
        """Return files directly imported by this file."""

        file_path = self._normalize_path(file_path)

        if file_path not in self.graph:
            return []

        return list(self.graph.successors(file_path))

    def get_dependents(self, file_path: str) -> list[str]:
        """Return files that directly depend on this file."""

        file_path = self._normalize_path(file_path)

        if file_path not in self.graph:
            return []

        return list(self.graph.predecessors(file_path))

    def get_impact(self, file_path: str) -> list[str]:
        """Return all transitive dependents affected by a file change."""

        file_path = self._normalize_path(file_path)

        if file_path not in self.graph:
            return []

        return list(nx.descendants(self.graph.reverse(copy=False), file_path))

    def get_summary(self) -> dict:
        """Return basic dependency graph statistics."""

        return {
            "total_files": self.graph.number_of_nodes(),
            "total_dependencies": self.graph.number_of_edges(),
            "is_acyclic": nx.is_directed_acyclic_graph(self.graph),
        }
