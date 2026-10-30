import pytest

from codemind.search.hybrid_report import HybridRetrievalEvaluator


def test_hybrid_retrieval_report():
    evaluator = HybridRetrievalEvaluator()

    relevant_ids = {
        "process_payment",
        "validate_payment",
        "refund_payment",
    }

    strategies = {
        "keyword": [
            "process_payment",
            "generate_report",
            "validate_payment",
        ],
        "semantic": [
            "validate_payment",
            "refund_payment",
            "process_payment",
        ],
        "hybrid": [
            "process_payment",
            "validate_payment",
            "refund_payment",
        ],
    }

    report = evaluator.evaluate(
        strategies=strategies,
        relevant_ids=relevant_ids,
        k=3,
    )

    assert report["total_strategies"] == 3
    assert report["total_relevant_documents"] == 3

    assert report["results"]["keyword"]["precision"] == pytest.approx(2 / 3)
    assert report["results"]["semantic"]["precision"] == 1.0
    assert report["results"]["hybrid"]["precision"] == 1.0


def test_rejects_empty_strategies():
    evaluator = HybridRetrievalEvaluator()

    with pytest.raises(ValueError):
        evaluator.evaluate({}, {"process_payment"})


def test_rejects_invalid_k():
    evaluator = HybridRetrievalEvaluator()

    with pytest.raises(ValueError):
        evaluator.evaluate(
            {"hybrid": ["process_payment"]},
            {"process_payment"},
            k=0,
        )
