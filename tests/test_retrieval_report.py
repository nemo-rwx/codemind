import pytest

from codemind.search.report import RetrievalEvaluator


def test_retrieval_evaluation_report():
    evaluator = RetrievalEvaluator()

    query_results = [
        {
            "query": "Find payment processing code",
            "retrieved_ids": [
                "payment_001",
                "report_001",
                "payment_002",
            ],
            "relevant_ids": {
                "payment_001",
                "payment_002",
            },
        },
        {
            "query": "Find employee reporting code",
            "retrieved_ids": [
                "image_001",
                "hr_001",
                "hr_002",
            ],
            "relevant_ids": {
                "hr_001",
                "hr_002",
            },
        },
    ]

    report = evaluator.evaluate(query_results, k=3)

    assert report["total_queries"] == 2
    assert report["k"] == 3

    assert report["average_precision"] == pytest.approx(2 / 3)
    assert report["average_recall"] == pytest.approx(1.0)
    assert report["mrr"] == pytest.approx(0.75)

    assert len(report["query_results"]) == 2


def test_retrieval_report_rejects_empty_input():
    evaluator = RetrievalEvaluator()

    with pytest.raises(ValueError):
        evaluator.evaluate([], k=3)


def test_retrieval_report_rejects_invalid_k():
    evaluator = RetrievalEvaluator()

    with pytest.raises(ValueError):
        evaluator.evaluate(
            [
                {
                    "query": "payment",
                    "retrieved_ids": ["payment_001"],
                    "relevant_ids": {"payment_001"},
                }
            ],
            k=0,
        )
