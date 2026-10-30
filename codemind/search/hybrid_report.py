from codemind.search.evaluation import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


class HybridRetrievalEvaluator:
    """Evaluate and compare multiple retrieval strategies."""

    def evaluate(
        self,
        strategies: dict[str, list[str]],
        relevant_ids: set[str],
        k: int = 3,
    ) -> dict:
        if not strategies:
            raise ValueError("At least one retrieval strategy is required")

        if not relevant_ids:
            raise ValueError("Relevant IDs cannot be empty")

        if k < 1:
            raise ValueError("k must be at least 1")

        report = {}

        for strategy, retrieved_ids in strategies.items():
            report[strategy] = {
                "precision": precision_at_k(retrieved_ids, relevant_ids, k),
                "recall": recall_at_k(retrieved_ids, relevant_ids, k),
                "mrr": reciprocal_rank(retrieved_ids, relevant_ids),
            }

        return {
            "total_strategies": len(strategies),
            "total_relevant_documents": len(relevant_ids),
            "k": k,
            "results": report,
        }
