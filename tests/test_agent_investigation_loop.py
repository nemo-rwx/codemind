from codemind.agent.graph import CodeMindAgent


class FakeAgentNodes:
    def __init__(self):
        self.selection_count = 0

    def select_tool(self, state):
        self.selection_count += 1

        if self.selection_count <= 2:
            return {
                "selected_tool": "search_symbols",
                "tool_input": f"query_{self.selection_count}",
            }

        return {
            "selected_tool": "answer_directly",
            "tool_input": "",
            "answer": "Investigation completed.",
        }

    def record_observation(self, state):
        observation = {
            "tool": state["selected_tool"],
            "input": state["tool_input"],
            "results": state["tool_result"],
            "errors": state["errors"],
        }

        return {"observations": state["observations"] + [observation]}

    def generate_answer(self, state):
        return {"answer": state["answer"] or "Investigation completed."}


class FakeToolExecutor:
    def __init__(self):
        self.execution_count = 0

    def execute(self, tool_name, tool_input, repository_path):
        self.execution_count += 1

        return {
            "tool_result": [{"name": f"Symbol{self.execution_count}"}],
            "errors": [],
        }


def test_agent_repeats_tool_execution():
    nodes = FakeAgentNodes()
    executor = FakeToolExecutor()

    agent = CodeMindAgent(
        nodes=nodes,
        tool_executor=executor,
        max_iterations=3,
    )

    result = agent.run(
        query="Investigate repository indexing",
        repository_path=".",
    )

    assert executor.execution_count == 2
    assert len(result["observations"]) == 2
    assert result["answer"] == "Investigation completed."


def test_agent_respects_iteration_limit():
    nodes = FakeAgentNodes()
    executor = FakeToolExecutor()

    agent = CodeMindAgent(
        nodes=nodes,
        tool_executor=executor,
        max_iterations=1,
    )

    result = agent.run(
        query="Investigate repository indexing",
        repository_path=".",
    )

    assert executor.execution_count == 1
    assert result["iteration"] == 1


def test_agent_rejects_zero_max_iterations():
    try:
        CodeMindAgent(max_iterations=0)
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "max_iterations" in str(error)
