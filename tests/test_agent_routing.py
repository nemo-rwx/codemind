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
        }

    def generate_answer(self, state):
        results = state["observations"][0]["results"]

        if not results:
            return {"answer": "No relevant code was found."}

        return {"answer": "Found relevant repository code."}


class FakeToolExecutor:
    def __init__(self, return_results=True):
        self.return_results = return_results

    def execute(self, tool_name, tool_input, repository_path):
        results = ["fake code chunk"] if self.return_results else []

        return {
            "tool_result": results,
            "errors": [],
        }


def test_agent_routes_to_answer_when_results_exist():
    agent = CodeMindAgent(
        nodes=FakeAgentNodes(),
        tool_executor=FakeToolExecutor(return_results=True),
        max_iterations=1,
    )

    result = agent.run(
        query="Explain indexing",
        repository_path=".",
    )

    assert result["answer"] == "Found relevant repository code."
    assert len(result["observations"]) == 1


def test_agent_routes_to_no_results_when_results_are_empty():
    agent = CodeMindAgent(
        nodes=FakeAgentNodes(),
        tool_executor=FakeToolExecutor(return_results=False),
        max_iterations=1,
    )

    result = agent.run(
        query="Explain something unavailable",
        repository_path=".",
    )

    assert result["answer"] == "No relevant code was found."
    assert result["observations"][0]["results"] == []
