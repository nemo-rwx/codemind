def precision_at_k(
    retrieved_ids: list[str],
    relevant_ids: set[str],
    k: int,
) -> float:
    """Calculate the fraction of top-k results that are relevant."""

    if k < 1:
        raise ValueError("k must be at least 1")

    if not relevant_ids:
        return 0.0

    top_results = retrieved_ids[:k]

    relevant_count = sum(
        1 for document_id in top_results if document_id in relevant_ids
    )

    return relevant_count / k


def recall_at_k(
    retrieved_ids: list[str],
    relevant_ids: set[str],
    k: int,
) -> float:
    """Calculate the fraction of relevant documents retrieved in top-k."""

    if k < 1:
        raise ValueError("k must be at least 1")

    if not relevant_ids:
        return 0.0

    top_results = set(retrieved_ids[:k])

    relevant_count = len(top_results & relevant_ids)

    return relevant_count / len(relevant_ids)


def reciprocal_rank(
    retrieved_ids: list[str],
    relevant_ids: set[str],
) -> float:
    """Calculate the reciprocal rank of the first relevant result."""

    for rank, document_id in enumerate(retrieved_ids, start=1):
        if document_id in relevant_ids:
            return 1.0 / rank

    return 0.0


def mean_reciprocal_rank(
    query_results: list[tuple[list[str], set[str]]],
) -> float:
    """Calculate the mean reciprocal rank across multiple queries."""

    if not query_results:
        return 0.0

    total_reciprocal_rank = sum(
        reciprocal_rank(retrieved_ids, relevant_ids)
        for retrieved_ids, relevant_ids in query_results
    )

    return total_reciprocal_rank / len(query_results)
