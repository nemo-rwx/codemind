from codemind.search.evaluation import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_compare_retrieval_strategies():
    relevant_ids = {
        "process_payment",
        "validate_payment",
        "refund_payment",
    }

    keyword_results = [
        "process_payment",
        "generate_report",
        "validate_payment",
    ]

    semantic_results = [
        "validate_payment",
        "refund_payment",
        "process_payment",
    ]

    hybrid_results = [
        "process_payment",
        "validate_payment",
        "refund_payment",
    ]

    strategies = {
        "keyword": keyword_results,
        "semantic": semantic_results,
        "hybrid": hybrid_results,
    }

    metrics = {}

    for strategy, results in strategies.items():
        metrics[strategy] = {
            "precision": precision_at_k(results, relevant_ids, k=3),
            "recall": recall_at_k(results, relevant_ids, k=3),
            "mrr": reciprocal_rank(results, relevant_ids),
        }

    assert metrics["keyword"]["precision"] == 2 / 3
    assert metrics["semantic"]["precision"] == 1.0
    assert metrics["hybrid"]["precision"] == 1.0

    assert metrics["keyword"]["recall"] == 2 / 3
    assert metrics["semantic"]["recall"] == 1.0
    assert metrics["hybrid"]["recall"] == 1.0

    assert metrics["keyword"]["mrr"] == 1.0
    assert metrics["semantic"]["mrr"] == 1.0
    assert metrics["hybrid"]["mrr"] == 1.0
