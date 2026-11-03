REPOSITORY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "hybrid_search",
            "description": (
                "Search actual repository code using both keyword and semantic "
                "retrieval. Use this FIRST for questions about implementation, "
                "algorithms, architecture, behavior, or how components work. "
                "Returns ranked files, symbols, and line numbers."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A natural-language description of the code or behavior to find.",
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_symbols",
            "description": (
                "Search indexed repository classes and functions by symbol name. "
                "Use for questions asking where a particular class or function is defined."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_symbol",
            "description": "Locate a specific class, function, or method.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol_name": {"type": "string"},
                },
                "required": ["symbol_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_source",
            "description": (
                "Retrieve actual source code from a repository-relative path "
                "and line range. Use after search to inspect implementation details."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "start_line": {"type": "integer"},
                    "end_line": {"type": "integer"},
                },
                "required": ["file_path", "start_line", "end_line"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_change",
            "description": (
                "Analyze a source file change and identify files that depend on it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                },
                "required": ["file_path"],
                "additionalProperties": False,
            },
        },
    },
]
