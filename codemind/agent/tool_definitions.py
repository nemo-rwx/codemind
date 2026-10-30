REPOSITORY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_symbols",
            "description": (
                "Search indexed repository classes and functions "
                "using a partial or exact symbol name."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Symbol name or search term.",
                    }
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
            "description": (
                "Locate a specific class, function, or method "
                "in the indexed repository."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol_name": {
                        "type": "string",
                        "description": "Exact or partial symbol name.",
                    }
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
                "Retrieve source code using a repository-relative "
                "file path and line numbers."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "start_line": {"type": "integer"},
                    "end_line": {"type": "integer"},
                },
                "required": [
                    "file_path",
                    "start_line",
                    "end_line",
                ],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_change",
            "description": (
                "Analyze a source file change and identify files "
                "that directly or indirectly depend on that file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": (
                            "Repository-relative path of the changed file."
                        ),
                    }
                },
                "required": ["file_path"],
                "additionalProperties": False,
            },
        },
    },
]
