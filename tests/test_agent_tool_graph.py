from codemind.agent.graph import CodeMindAgent


class FakeAgentNodes:
    def select_tool(self, state):
        return {
            "selected_tool": "search_symbols",
            "tool_input": state["query"],
        }

    def generate_answer(self, state):
        return {"answer": (f"Found {len(state['tool_result'])} repository results.")}


class FakeToolExecutor:
    def execute(self, state):
        return {
            "tool_result": [{"name": "RepositoryIndexer"}],
            "errors": [],
        }


def test_agent_executes_tool_workflow():
    agent = CodeMindAgent(
        nodes=FakeAgentNodes(),
        tool_executor=FakeToolExecutor(),
    )

    result = agent.run(
        query="Find RepositoryIndexer",
        repository_path=".",
    )

    assert result["selected_tool"] == "search_symbols"
    assert result["tool_result"][0]["name"] == "RepositoryIndexer"
    assert result["answer"] == "Found 1 repository results."


def test_agent_rejects_empty_query():
    agent = CodeMindAgent(
        nodes=FakeAgentNodes(),
        tool_executor=FakeToolExecutor(),
    )

    try:
        agent.run(
            query=" ",
            repository_path=".",
        )
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "Query" in str(error)


def test_agent_rejects_invalid_top_k():
    agent = CodeMindAgent(
        nodes=FakeAgentNodes(),
        tool_executor=FakeToolExecutor(),
    )

    try:
        agent.run(
            query="Explain indexing",
            repository_path=".",
            top_k=0,
        )
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "top_k" in str(error)
