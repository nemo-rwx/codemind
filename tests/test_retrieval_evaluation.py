import pytest

from codemind.search.evaluation import (
    precision_at_k,
    recall_at_k,
)


def test_precision_at_k():
    retrieved = ["payment", "report", "image", "invoice"]
    relevant = {"payment", "invoice"}

    result = precision_at_k(retrieved, relevant, k=4)

    assert result == 0.5


def test_recall_at_k():
    retrieved = ["payment", "report", "image"]
    relevant = {"payment", "invoice"}

    result = recall_at_k(retrieved, relevant, k=3)

    assert result == 0.5


def test_precision_at_k_with_no_relevant_documents():
    result = precision_at_k(
        ["payment", "report"],
        set(),
        k=2,
    )

    assert result == 0.0


def test_recall_at_k_with_no_relevant_documents():
    result = recall_at_k(
        ["payment", "report"],
        set(),
        k=2,
    )

    assert result == 0.0


def test_precision_rejects_invalid_k():
    with pytest.raises(ValueError):
        precision_at_k(["payment"], {"payment"}, k=0)


def test_recall_rejects_invalid_k():
    with pytest.raises(ValueError):
        recall_at_k(["payment"], {"payment"}, k=0)


from codemind.search.evaluation import (
    reciprocal_rank,
    mean_reciprocal_rank,
)


def test_reciprocal_rank_first_result():
    result = reciprocal_rank(
        ["payment", "report", "image"],
        {"payment"},
    )

    assert result == 1.0


def test_reciprocal_rank_third_result():
    result = reciprocal_rank(
        ["report", "image", "payment"],
        {"payment"},
    )

    assert result == 1 / 3


def test_reciprocal_rank_not_found():
    result = reciprocal_rank(
        ["report", "image"],
        {"payment"},
    )

    assert result == 0.0


def test_mean_reciprocal_rank():
    query_results = [
        (["payment", "report"], {"payment"}),
        (["report", "payment"], {"payment"}),
        (["image", "report"], {"payment"}),
    ]

    result = mean_reciprocal_rank(query_results)

    expected = (1.0 + 0.5 + 0.0) / 3

    assert abs(result - expected) < 0.000001


def test_mean_reciprocal_rank_empty_input():
    assert mean_reciprocal_rank([]) == 0.0
