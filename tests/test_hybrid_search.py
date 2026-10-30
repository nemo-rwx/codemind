from codemind.search.hybrid import HybridSearchService


class FakeKeywordSearch:
    def search(self, query):
        return [
            {
                "name": "process_payment",
                "kind": "function",
                "file_path": "payments.py",
                "language": "python",
                "start_line": 1,
                "end_line": 5,
                "parameters": "amount",
            },
            {
                "name": "generate_report",
                "kind": "function",
                "file_path": "reports.py",
                "language": "python",
                "start_line": 10,
                "end_line": 15,
                "parameters": None,
            },
        ]


class FakeSemanticSearch:
    def search(self, query, top_k=5):
        return [
            {
                "text": "def process_payment(amount): ...",
                "distance": 0.1,
                "metadata": {
                    "symbol": "process_payment",
                    "kind": "function",
                    "file_path": "payments.py",
                    "language": "python",
                    "start_line": 1,
                    "end_line": 5,
                },
            },
            {
                "text": "def refund_payment(amount): ...",
                "distance": 0.2,
                "metadata": {
                    "symbol": "refund_payment",
                    "kind": "function",
                    "file_path": "payments.py",
                    "language": "python",
                    "start_line": 20,
                    "end_line": 25,
                },
            },
        ]


def test_hybrid_search_combines_results():
    service = HybridSearchService(
        keyword_search=FakeKeywordSearch(),
        semantic_search=FakeSemanticSearch(),
    )

    results = service.search("payment", top_k=3)

    assert len(results) == 3

    # Appears in both retrieval systems.
    payment = next(result for result in results if result["name"] == "process_payment")

    assert set(payment["sources"]) == {"keyword", "semantic"}
    assert payment["text"] is not None

    # RRF should give the shared result a higher score.
    assert payment["score"] > results[1]["score"]


def test_hybrid_search_rejects_empty_query():
    service = HybridSearchService(
        keyword_search=FakeKeywordSearch(),
        semantic_search=FakeSemanticSearch(),
    )

    try:
        service.search("")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_hybrid_search_rejects_invalid_top_k():
    service = HybridSearchService(
        keyword_search=FakeKeywordSearch(),
        semantic_search=FakeSemanticSearch(),
    )

    try:
        service.search("payment", top_k=0)
        assert False, "Expected ValueError"
    except ValueError:
        pass
