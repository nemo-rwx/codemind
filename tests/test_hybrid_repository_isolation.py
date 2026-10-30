from codemind.search.hybrid import HybridSearchService


class FakeKeywordSearch:
    def search(self, query, repository_path=None):
        return [
            {
                "name": "process_payment",
                "kind": "function",
                "file_path": "payments.py",
                "root_path": "C:/projects/ecommerce",
                "language": "python",
                "start_line": 1,
                "end_line": 5,
                "parameters": "amount",
            }
        ]


class FakeSemanticSearch:
    def search(self, query, top_k=5, repository_path=None):
        return [
            {
                "text": "def process_payment(amount): ...",
                "distance": 0.1,
                "metadata": {
                    "symbol": "process_payment",
                    "kind": "function",
                    "file_path": "payments.py",
                    "repository": "C:/projects/ecommerce",
                    "language": "python",
                    "start_line": 1,
                    "end_line": 5,
                },
            }
        ]


def test_hybrid_search_respects_repository_filter():
    keyword = FakeKeywordSearch()
    semantic = FakeSemanticSearch()

    service = HybridSearchService(
        keyword_search=keyword,
        semantic_search=semantic,
    )

    results = service.search(
        "payment",
        repository_path="C:/projects/ecommerce",
    )

    assert len(results) == 1
    assert results[0]["repository"] == "C:/projects/ecommerce"
    assert set(results[0]["sources"]) == {"keyword", "semantic"}
