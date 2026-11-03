# Contributing

## Setup

```bash
git clone https://github.com/nemo-rwx/codemind.git
cd codemind
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
pip install -e ".[dev]"
cp .env.example .env        # add your OpenRouter key
```

## Running tests

```bash
pytest -v
```

## Code style

```bash
ruff check .
ruff format .
```

## Project structure

```
codemind/
  agent/        LangGraph agent, tools, guardrails
  api/          FastAPI app, routes, middleware
  chunking/     Code chunking for embeddings
  cli/          Typer CLI commands
  database/     SQLite schema, repositories, analytics
  embeddings/   Sentence Transformers wrapper
  graph/        Dependency graph (NetworkX)
  indexer/      Orchestrates scan + parse + store
  llm/          OpenRouter HTTP client
  parser/       Tree-sitter parser (Python + Java)
  rag/          Prompt builder, retrieval models
  scanner/      Repository file walker
  search/       Keyword, semantic, hybrid search
  telemetry.py  Anonymous usage events
  vectorstore/  ChromaDB wrapper
```

## Adding a new language

1. Install the Tree-sitter grammar: `pip install tree-sitter-<lang>`
2. Add the parser to `CodeParser.__init__` in `parser/service.py`
3. Add the extension to `SUPPORTED_EXTENSIONS` in `indexer/service.py` and `indexer/semantic.py`

## Adding a new agent tool

1. Add the tool definition to `agent/tool_definitions.py`
2. Add it to `GuardrailService.ALLOWED_TOOLS` in `agent/guardrails.py`
3. Implement validation in `GuardrailService.validate_tool_call`
4. Implement execution in `ToolExecutor.execute` in `agent/tool_executor.py`
5. Handle argument extraction in `AgentNodes.select_tool` in `agent/nodes.py`
