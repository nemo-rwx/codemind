from typing import Any

from langgraph.graph import END, START, StateGraph

from codemind.agent.nodes import AgentNodes
from codemind.agent.state import AgentState
from codemind.agent.tool_executor import ToolExecutor


class CodeMindAgent:
    """Agentic workflow for investigating and understanding repositories."""

    def __init__(
        self,
        nodes: AgentNodes | None = None,
        tool_executor: ToolExecutor | None = None,
        max_iterations: int = 5,
    ):
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")

        self.nodes = nodes or AgentNodes()
        self.tool_executor = tool_executor or self.nodes.tool_executor
        self.max_iterations = max_iterations

        self.graph = self._build_graph()

    def _build_graph(self):
        """Build and compile the LangGraph workflow."""

        workflow = StateGraph(AgentState)

        workflow.add_node("select_tool", self._select_tool)
        workflow.add_node("execute_tool", self._execute_tool)
        workflow.add_node("record_observation", self._record_observation)
        workflow.add_node("generate_answer", self._generate_answer)

        workflow.add_edge(START, "select_tool")

        workflow.add_conditional_edges(
            "select_tool",
            self._route_after_selection,
            {
                "execute_tool": "execute_tool",
                "generate_answer": "generate_answer",
            },
        )

        workflow.add_edge("execute_tool", "record_observation")

        workflow.add_conditional_edges(
            "record_observation",
            self._route_after_observation,
            {
                "select_tool": "select_tool",
                "generate_answer": "generate_answer",
            },
        )

        workflow.add_edge("generate_answer", END)

        return workflow.compile()

    def _select_tool(self, state: AgentState) -> dict[str, Any]:
        """Select a repository tool."""

        return self.nodes.select_tool(state)

    def _execute_tool(self, state: AgentState) -> dict[str, Any]:
        """Execute the selected tool and increment the iteration counter."""

        current_iteration = state.get("iteration", 0)

        try:
            result = self.tool_executor.execute(
                tool_name=state["selected_tool"],
                tool_input=state["tool_input"],
                repository_path=state["repository_path"],
            )

            if not isinstance(result, dict):
                raise TypeError("Tool executor must return a dictionary")

            updates = dict(result)

        except Exception as error:  # noqa: BLE001
            # Convert unexpected tool failures into agent state errors.
            updates = {
                "tool_result": [],
                "errors": state.get("errors", []) + [f"Tool execution failed: {error}"],
            }

        updates["iteration"] = current_iteration + 1

        return updates

    def _record_observation(self, state: AgentState) -> dict[str, Any]:
        """Record the tool result in the agent's observation history."""

        try:
            return self.nodes.record_observation(state)

        except (TypeError, ValueError, KeyError) as error:
            observation = {
                "tool": state.get("selected_tool", ""),
                "result": f"Could not record observation: {error}",
            }

            observations = list(state.get("observations", []))
            observations.append(observation)

            return {
                "observations": observations,
                "errors": state.get("errors", [])
                + [f"Observation recording failed: {error}"],
            }

    def _generate_answer(self, state: AgentState) -> dict[str, Any]:
        """Generate the final answer."""

        try:
            return self.nodes.generate_answer(state)

        except (RuntimeError, TypeError, ValueError, KeyError) as error:
            return {
                "answer": (
                    "I could not generate a complete answer because "
                    f"an error occurred: {error}"
                ),
                "errors": state.get("errors", [])
                + [f"Answer generation failed: {error}"],
            }

    def _route_after_selection(self, state: AgentState) -> str:
        """Decide whether a tool can be executed."""

        if state.get("errors"):
            return "generate_answer"

        if not state.get("selected_tool"):
            return "generate_answer"

        if state.get("iteration", 0) >= state.get(
            "max_iterations", self.max_iterations
        ):
            return "generate_answer"

        return "execute_tool"

    def _route_after_observation(self, state: AgentState) -> str:
        """Decide whether to continue investigating or answer."""

        if state.get("errors"):
            return "generate_answer"

        if state.get("iteration", 0) >= state.get(
            "max_iterations", self.max_iterations
        ):
            return "generate_answer"

        return "select_tool"

    def run(
        self,
        query: str,
        repository_path: str,
        top_k: int = 5,
    ) -> AgentState:
        """Run the CodeMind agent against a repository."""

        if not isinstance(query, str):
            raise TypeError("Query must be a string")

        if not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        initial_state: AgentState = {
            "query": query.strip(),
            "repository_path": repository_path,
            "top_k": top_k,
            "selected_tool": "",
            "tool_input": "",
            "tool_result": [],
            "observations": [],
            "iteration": 0,
            "max_iterations": self.max_iterations,
            "answer": "",
            "errors": [],
        }

        return self.graph.invoke(initial_state)
