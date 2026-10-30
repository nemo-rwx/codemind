from codemind.agent.tool_executor import ToolExecutor


class FakeRepositoryTools:
    def search_symbols(self, query, repository_path):
        return [
            {
                "name": "RepositoryIndexer",
                "kind": "class",
                "file_path": "indexer/service.py",
                "language": "python",
                "start_line": 10,
                "end_line": 50,
            }
        ]

    def find_symbol(self, symbol_name, repository_path):
        return [
            {
                "name": symbol_name,
                "kind": "function",
                "file_path": "service.py",
                "language": "python",
                "start_line": 5,
                "end_line": 15,
            }
        ]


def test_execute_search_symbols():
    executor = ToolExecutor(FakeRepositoryTools())

    result = executor.execute(
        {
            "selected_tool": "search_symbols",
            "tool_input": "RepositoryIndexer",
            "repository_path": ".",
        }
    )

    assert result["tool_result"][0]["name"] == "RepositoryIndexer"
    assert result["errors"] == []


def test_execute_find_symbol():
    executor = ToolExecutor(FakeRepositoryTools())

    result = executor.execute(
        {
            "selected_tool": "find_symbol",
            "tool_input": "PaymentService",
            "repository_path": ".",
        }
    )

    assert result["tool_result"][0]["name"] == "PaymentService"


def test_reject_unknown_tool():
    executor = ToolExecutor(FakeRepositoryTools())

    result = executor.execute(
        {
            "selected_tool": "delete_files",
            "tool_input": "anything",
            "repository_path": ".",
        }
    )

    assert result["tool_result"] == []
    assert "Tool not allowed" in result["errors"][0]
