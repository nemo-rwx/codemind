from typing import TypedDict


class AgentState(TypedDict):
    """Shared state for the CodeMind agent."""

    query: str
    repository_path: str
    top_k: int

    selected_tool: str
    tool_input: str

    tool_result: list[dict]
    observations: list[dict]

    iteration: int
    max_iterations: int

    answer: str
    errors: list[str]
