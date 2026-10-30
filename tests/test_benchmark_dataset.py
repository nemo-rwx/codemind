import json

import pytest

from codemind.search.dataset import BenchmarkDataset


def test_load_valid_dataset(tmp_path):
    dataset = {
        "top_k": 3,
        "queries": [
            {
                "query": "Find payment processing",
                "relevant_ids": ["payments.py::process_payment::10"],
            }
        ],
    }

    dataset_path = tmp_path / "dataset.json"
    dataset_path.write_text(json.dumps(dataset), encoding="utf-8")

    result = BenchmarkDataset.load(dataset_path)

    assert result["top_k"] == 3
    assert len(result["queries"]) == 1


def test_rejects_missing_dataset():
    with pytest.raises(FileNotFoundError):
        BenchmarkDataset.load("missing_dataset.json")


def test_rejects_empty_queries(tmp_path):
    dataset_path = tmp_path / "dataset.json"
    dataset_path.write_text(
        json.dumps({"queries": []}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        BenchmarkDataset.load(dataset_path)


def test_rejects_invalid_relevant_ids(tmp_path):
    dataset_path = tmp_path / "dataset.json"
    dataset_path.write_text(
        json.dumps(
            {
                "queries": [
                    {
                        "query": "Find payment processing",
                        "relevant_ids": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        BenchmarkDataset.load(dataset_path)
