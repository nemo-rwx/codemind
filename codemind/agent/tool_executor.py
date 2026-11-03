from codemind.agent.guardrails import (
    GuardrailError,
    GuardrailService,
)
from codemind.agent.tools.repository_tools import RepositoryTools


class ToolExecutor:
    """Validate and execute read-only repository tools."""

    def __init__(
        self,
        repository_tools=None,
        guardrails=None,
    ):
        self.repository_tools = repository_tools or RepositoryTools()
        self.guardrails = guardrails or GuardrailService()

    def execute(
        self,
        tool_name: str,
        tool_input: str,
        repository_path: str,
    ) -> dict:
        try:
            arguments = self.guardrails.validate_tool_call(
                tool_name=tool_name,
                tool_input=tool_input,
                repository_path=repository_path,
            )

            if tool_name == "hybrid_search":
                result = self.repository_tools.hybrid_search(
                    query=arguments["query"],
                    repository_path=repository_path,
                )

            elif tool_name == "search_symbols":
                result = self.repository_tools.search_symbols(
                    query=arguments["query"],
                    repository_path=repository_path,
                )

            elif tool_name == "find_symbol":
                result = self.repository_tools.find_symbol(
                    symbol_name=arguments["query"],
                    repository_path=repository_path,
                )

            elif tool_name == "get_source":
                result = self.repository_tools.get_source(
                    repository_path=repository_path,
                    file_path=arguments["file_path"],
                    start_line=arguments["start_line"],
                    end_line=arguments["end_line"],
                )

            elif tool_name == "analyze_change":
                result = self.repository_tools.analyze_change(
                    repository_path=repository_path,
                    file_path=arguments["file_path"],
                )

            else:
                raise GuardrailError("Unsupported tool")

            return {
                "tool_result": (result if isinstance(result, list) else [result]),
                "errors": [],
            }

        except (
            GuardrailError,
            ValueError,
            OSError,
            KeyError,
        ) as error:
            return {
                "tool_result": [],
                "errors": [str(error)],
            }
