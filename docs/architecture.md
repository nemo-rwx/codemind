# Architecture

## Overview

CodeMind is structured as a layered system: a CLI and REST API on top, a LangGraph agent in the middle, and search, parsing, and storage services at the bottom.

```
┌─────────────────────────────────────┐
│         CLI  (Typer + Rich)         │
│         API  (FastAPI)              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         CodeMind Agent              │
│    (LangGraph state machine)        │
│                                     │
│  select_tool → execute_tool         │
│       → record_observation          │
│       → generate_answer             │
└──────┬──────────────┬───────────────┘
       │              │
┌──────▼──────┐ ┌─────▼───────────────┐
│   Search    │ │   RAG / Prompt      │
│  Services   │ │   Builder           │
│             │ └─────────────────────┘
│ - Keyword   │
│ - Semantic  │
│ - Hybrid    │
└──────┬──────┘
       │
┌──────▼──────────────────────────────┐
│           Storage                   │
│                                     │
│  SQLite (symbols, imports, calls)   │
│  ChromaDB (embeddings)              │
└──────┬──────────────────────────────┘
       │
┌──────▼──────────────────────────────┐
│        Parser + Scanner             │
│                                     │
│  Tree-sitter (Python, Java)         │
│  Sentence Transformers (embeddings) │
└─────────────────────────────────────┘
```

## Modules

### `scanner`
Walks a repository directory tree, detects languages by file extension, and returns file metadata. Skips `.git`, `node_modules`, `__pycache__`, and other generated directories.

### `parser`
Uses Tree-sitter to parse Python and Java source files. Extracts classes, functions, methods, imports, and function calls into structured models.

### `database`
SQLite-backed storage for repositories, source files, symbols, imports, and calls. Schema initializes automatically on first use. Also stores API analytics events.

### `vectorstore`
ChromaDB-backed vector store for semantic search. Stores code chunk embeddings with metadata (file path, symbol name, line range).

### `embeddings`
Wraps `sentence-transformers` (`BAAI/bge-small-en-v1.5`) to generate normalized embeddings for code chunks and queries.

### `chunking`
Splits parsed files into overlapping code chunks suitable for embedding.

### `indexer`
Orchestrates scanning, parsing, and persisting to SQLite (`RepositoryIndexer`) and ChromaDB (`SemanticIndexer`).

### `search`
Three search strategies:
- **Keyword** (`CodeSearchService`) — SQLite `LIKE` query on symbol names
- **Semantic** (`SemanticSearchService`) — ChromaDB cosine similarity search
- **Hybrid** (`HybridSearchService`) — combines both using Reciprocal Rank Fusion (RRF)

### `agent`
LangGraph state machine with four nodes:
- `select_tool` — LLM chooses which repository tool to call
- `execute_tool` — runs the chosen tool with guardrail validation
- `record_observation` — stores sanitized tool output in agent state
- `generate_answer` — LLM generates a grounded answer from accumulated observations

Available tools: `search_symbols`, `find_symbol`, `get_source`, `analyze_change`.

### `graph`
NetworkX-based directed dependency graph. Resolves Python and Java imports to build file-level dependency edges. Used by `analyze_change` to find transitive dependents.

### `rag`
Builds structured prompts from retrieved code context. Enforces grounding rules — the LLM is instructed to cite sources and never invent details.

### `llm`
HTTP client for the OpenRouter API. Supports standard chat completion and tool-calling.

### `telemetry`
Anonymous usage event capture via PostHog. Fires `codemind_ask` events with success flag, iteration count, query length, OS, and Python version. Respects `CODEMIND_TELEMETRY=off`.

### `api`
FastAPI application with analytics middleware, repository scan endpoint, and analytics endpoint.

## Security

- **Path traversal prevention** — all file paths are resolved and checked to be within the repository root before use
- **Prompt injection detection** — tool outputs are scanned for injection patterns before being passed to the LLM
- **Secret redaction** — API keys and tokens in tool outputs are redacted before being included in prompts
- **Input validation** — all tool inputs are validated by `GuardrailService` before execution
