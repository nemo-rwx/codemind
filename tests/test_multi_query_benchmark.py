import pytest

from codemind.search.benchmark import RetrievalBenchmark


def test_evaluate_multiple_queries():
    benchmark = RetrievalBenchmark()

    def fake_evaluate_query(
        query,
        relevant_ids,
        repository_path,
        k=3,
    ):
        return {
            "results": {
                "keyword": {
                    "precision": 0.5,
                    "recall": 0.5,
                    "mrr": 1.0,
                },
                "semantic": {
                    "precision": 1.0,
                    "recall": 1.0,
                    "mrr": 1.0,
                },
                "hybrid": {
                    "precision": 1.0,
                    "recall": 1.0,
                    "mrr": 1.0,
                },
            }
        }

    benchmark.evaluate_query = fake_evaluate_query

    queries = [
        {
            "query": "Find payment processing",
            "relevant_ids": {"payments.py::process_payment::10"},
        },
        {
            "query": "Find payment validation",
            "relevant_ids": {"payments.py::validate_payment::20"},
        },
    ]

    report = benchmark.evaluate_multiple(
        queries=queries,
        repository_path=".",
        k=3,
    )

    assert report["total_queries"] == 2
    assert report["aggregate"]["keyword"]["precision"] == 0.5
    assert report["aggregate"]["semantic"]["precision"] == 1.0
    assert report["aggregate"]["hybrid"]["precision"] == 1.0


def test_rejects_empty_query_list():
    benchmark = RetrievalBenchmark()

    with pytest.raises(ValueError):
        benchmark.evaluate_multiple(
            queries=[],
            repository_path=".",
        )
