from codemind.search.evaluation import (
    mean_reciprocal_rank,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


class RetrievalEvaluator:
    """Evaluate retrieval results using standard ranking metrics."""

    def evaluate(
        self,
        query_results: list[dict],
        k: int = 3,
    ) -> dict:
        if k < 1:
            raise ValueError("k must be at least 1")

        if not query_results:
            raise ValueError("Query results cannot be empty")

        evaluated_queries = []
        reciprocal_rank_inputs = []

        for item in query_results:
            retrieved_ids = item["retrieved_ids"]
            relevant_ids = item["relevant_ids"]

            precision = precision_at_k(
                retrieved_ids,
                relevant_ids,
                k,
            )

            recall = recall_at_k(
                retrieved_ids,
                relevant_ids,
                k,
            )

            rr = reciprocal_rank(
                retrieved_ids,
                relevant_ids,
            )

            evaluated_queries.append(
                {
                    "query": item["query"],
                    "precision_at_k": precision,
                    "recall_at_k": recall,
                    "reciprocal_rank": rr,
                }
            )

            reciprocal_rank_inputs.append((retrieved_ids, relevant_ids))

        total_queries = len(evaluated_queries)

        average_precision = (
            sum(item["precision_at_k"] for item in evaluated_queries) / total_queries
        )

        average_recall = (
            sum(item["recall_at_k"] for item in evaluated_queries) / total_queries
        )

        mrr = mean_reciprocal_rank(reciprocal_rank_inputs)

        return {
            "total_queries": total_queries,
            "k": k,
            "average_precision": average_precision,
            "average_recall": average_recall,
            "mrr": mrr,
            "query_results": evaluated_queries,
        }
