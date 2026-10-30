import json
from pathlib import Path
from typing import Any


def load_dataset(dataset_path: str | Path) -> list[dict[str, Any]]:
    """Load and validate a retrieval benchmark dataset."""

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
        raise ValueError("Dataset must contain a queries list")

    validated_queries = []

    for index, item in enumerate(queries):
        if not isinstance(item, dict):
            raise TypeError(f"Invalid query at index {index}")

        query = item.get("query")
        relevant = item.get("relevant", [])

        if not isinstance(query, str) or not query.strip():
            raise ValueError(f"Query at index {index} must be a non-empty string")

        if not isinstance(relevant, list):
            raise ValueError(f"Relevant documents at index {index} must be a list")

        if not all(isinstance(document_id, str) for document_id in relevant):
            raise TypeError(f"Relevant document IDs at index {index} must be strings")

        validated_queries.append(
            {
                **item,
                "query": query.strip(),
                "relevant": relevant,
            }
        )

    return validated_queries
