from codemind.agent.graph import CodeMindAgent


class FakeAgentNodes:
    def select_tool(self, state):
        return {
            "selected_tool": "search_symbols",
            "tool_input": "indexing",
        }

    def record_observation(self, state):
        observation = {
            "tool": state["selected_tool"],
            "input": state["tool_input"],
            "results": state["tool_result"],
            "errors": state["errors"],
        }

        return {
            "observations": state["observations"] + [observation],
            "iteration": state.get("iteration", 0) + 1,
        }

    def generate_answer(self, state):
        assert state["observations"][0]["results"] == ["fake code chunk"]

        return {"answer": "Repository indexing scans and parses source files."}


class FakeToolExecutor:
    def execute(self, state):
        return {
            "tool_result": ["fake code chunk"],
            "errors": [],
            "iteration": state.get("iteration", 0) + 1,
        }


def test_agent_graph_executes_nodes():
    agent = CodeMindAgent(
        nodes=FakeAgentNodes(),
        tool_executor=FakeToolExecutor(),
        max_iterations=1,
    )

    result = agent.run(
        query="How does repository indexing work?",
        repository_path=".",
        top_k=3,
    )

    assert result["answer"] == ("Repository indexing scans and parses source files.")
    assert len(result["observations"]) == 1


def test_agent_rejects_empty_query():
    agent = CodeMindAgent(
        nodes=FakeAgentNodes(),
        tool_executor=FakeToolExecutor(),
    )

    try:
        agent.run(query=" ", repository_path=".")
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
