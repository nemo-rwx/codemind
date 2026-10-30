import pytest

from codemind.agent.tools.repository_tools import RepositoryTools


class FakeSearchService:
    def search(self, query, repository_path=None):
        return [
            {
                "name": "RepositoryIndexer",
                "kind": "class",
                "file_path": "indexer/service.py",
                "start_line": 10,
            }
        ]


def test_search_symbols():
    tools = RepositoryTools(search_service=FakeSearchService())

    results = tools.search_symbols(
        query="RepositoryIndexer",
        repository_path=".",
    )

    assert len(results) == 1
    assert results[0]["name"] == "RepositoryIndexer"


def test_find_symbol():
    tools = RepositoryTools(search_service=FakeSearchService())

    results = tools.find_symbol(
        symbol_name="RepositoryIndexer",
        repository_path=".",
    )

    assert results[0]["kind"] == "class"


def test_rejects_empty_query():
    tools = RepositoryTools(search_service=FakeSearchService())

    with pytest.raises(ValueError):
        tools.search_symbols(
            query=" ",
            repository_path=".",
        )


def test_rejects_empty_symbol_name():
    tools = RepositoryTools(search_service=FakeSearchService())

    with pytest.raises(ValueError):
        tools.find_symbol(
            symbol_name=" ",
            repository_path=".",
        )
