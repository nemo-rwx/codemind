from pathlib import Path

from codemind.search.dataset import load_dataset
from codemind.search.hybrid import HybridSearchService
from codemind.search.hybrid_report import HybridRetrievalEvaluator
from codemind.search.semantic import SemanticSearchService
from codemind.search.service import CodeSearchService


class RetrievalBenchmark:
    """Benchmark keyword, semantic, and hybrid retrieval."""

    def __init__(self):
        self.keyword_search = CodeSearchService()
        self.semantic_search = SemanticSearchService()
        self.hybrid_search = HybridSearchService()
        self.evaluator = HybridRetrievalEvaluator()

    def evaluate_query(
        self,
        query: str,
        relevant_ids: set[str],
        repository_path: str | Path,
        k: int = 3,
    ) -> dict:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        repository_path = str(Path(repository_path).expanduser().resolve())

        keyword_results = self.keyword_search.search(
            query, repository_path=repository_path
        )
        semantic_results = self.semantic_search.search(
            query, top_k=k, repository_path=repository_path
        )
        hybrid_results = self.hybrid_search.search(
            query, top_k=k, repository_path=repository_path
        )

        strategies = {
            "keyword": [self._document_id(result) for result in keyword_results[:k]],
            "semantic": [self._document_id(result) for result in semantic_results],
            "hybrid": [self._document_id(result) for result in hybrid_results],
        }

        return self.evaluator.evaluate(
            strategies=strategies,
            relevant_ids=relevant_ids,
            k=k,
        )

    def evaluate_multiple(
        self,
        queries: list[dict],
        repository_path: str | Path,
        k: int = 3,
    ) -> dict:
        if not queries:
            raise ValueError("At least one benchmark query is required")

        individual_reports = []

        for item in queries:
            report = self.evaluate_query(
                query=item["query"],
                relevant_ids=set(item["relevant"]),
                repository_path=repository_path,
                k=k,
            )

            individual_reports.append(
                {
                    "query": item["query"],
                    "results": report["results"],
                }
            )

        strategies = ("keyword", "semantic", "hybrid")
        aggregate = {}

        for strategy in strategies:
            aggregate[strategy] = {
                metric: sum(
                    report["results"][strategy][metric] for report in individual_reports
                )
                / len(individual_reports)
                for metric in ("precision", "recall", "mrr")
            }

        return {
            "total_queries": len(individual_reports),
            "k": k,
            "individual_reports": individual_reports,
            "aggregate": aggregate,
        }

    def evaluate_dataset(self, dataset_path: Path) -> dict:
        """Evaluate all queries from a benchmark dataset."""

        dataset_path = Path(dataset_path).expanduser().resolve()
        queries = load_dataset(dataset_path)

        repository_path = dataset_path.parent

        return self.evaluate_multiple(
            queries=queries,
            repository_path=repository_path,
            k=3,
        )

    @staticmethod
    def _document_id(result: dict) -> str:
        if "metadata" in result:
            metadata = result["metadata"]
            return (
                f"{metadata.get('file_path')}::"
                f"{metadata.get('symbol')}::"
                f"{metadata.get('start_line')}"
            )

        return (
            f"{result.get('file_path')}::"
            f"{result.get('name')}::"
            f"{result.get('start_line')}"
        )
