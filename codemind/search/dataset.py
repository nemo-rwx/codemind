import json
from pathlib import Path
from typing import Any


class BenchmarkDataset:
    """Load and validate retrieval benchmark datasets."""

    @staticmethod
    def load(dataset_path: str | Path) -> dict[str, Any]:
        """Load a benchmark dataset and validate its structure."""

        path = Path(dataset_path)

        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")

        if not path.is_file():
            raise ValueError(f"Dataset path is not a file: {path}")

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON dataset: {error}") from error

        if not isinstance(data, dict):
            raise TypeError("Dataset must contain a JSON object")

        queries = data.get("queries")

        if not isinstance(queries, list):
            raise TypeError("Dataset must contain a queries list")

        if not queries:
            raise ValueError("Dataset queries cannot be empty")

        top_k = data.get("top_k", 5)

        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
            raise ValueError("top_k must be a positive integer")

        validated_queries = []

        for index, item in enumerate(queries):
            if not isinstance(item, dict):
                raise TypeError(f"Invalid query at index {index}")

            query = item.get("query")
            relevant_ids = item.get(
                "relevant_ids",
                item.get("relevant"),
            )

            if not isinstance(query, str) or not query.strip():
                raise ValueError(f"Query at index {index} must be a non-empty string")

            if not isinstance(relevant_ids, list) or not relevant_ids:
                raise ValueError(
                    f"Relevant IDs at index {index} must be a non-empty list"
                )

            if not all(
                isinstance(document_id, str) and document_id.strip()
                for document_id in relevant_ids
            ):
                raise ValueError(
                    f"Relevant IDs at index {index} must contain non-empty strings"
                )

            validated_queries.append(
                {
                    **item,
                    "query": query.strip(),
                    "relevant_ids": relevant_ids,
                }
            )

        return {
            **data,
            "top_k": top_k,
            "queries": validated_queries,
        }


def load_dataset(dataset_path: str | Path) -> list[dict[str, Any]]:
    """Backward-compatible function returning validated queries."""

    dataset = BenchmarkDataset.load(dataset_path)
    return dataset["queries"]
