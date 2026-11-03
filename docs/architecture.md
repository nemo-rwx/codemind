# Architecture

## Overview

CodeMind is structured as a layered system: a CLI and REST API on top, a LangGraph agent in the middle, and search, parsing, and storage services at the bottom.

```
┌─────────────────────────────────────────────────┐
│           CLI  (Typer + Rich)                   │
│           API  (FastAPI on Render)              │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│              CodeMind Agent                     │
│         (LangGraph state machine)               │
│                                                 │
│  select_tool → execute_tool                     │
│       → record_observation                      │
│       → generate_answer                         │
└──────┬───────────────────────┬───────────────────┘
       │                       │
┌──────▼──────┐       ┌────────▼────────────────┐
│   Search    │       │   RAG / Prompt Builder  │
│  Services   │       └─────────────────────────┘
│             │
│ - Keyword   │
│ - Semantic  │
│ - Hybrid    │
└──────┬──────┘
       │
┌──────▼──────────────────────────────────────────┐
│                  Storage                        │
│                                                 │
│  SQLite    — symbols, imports, calls, analytics │
│  ChromaDB  — code embeddings                    │
│  PostHog   — usage telemetry events             │
└──────┬──────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────┐
│           Parser + Scanner                      │
│                                                 │
│  Tree-sitter (Python + Java)                    │
│  Sentence Transformers (embeddings)             │
│  OpenRouter (LLM via HTTP)                      │
└─────────────────────────────────────────────────┘
```

## Modules

### `scanner`
Walks a repository directory tree, detects languages by file extension, and returns file metadata. Skips `.git`, `node_modules`, `__pycache__`, and other generated directories.

### `parser`
Uses Tree-sitter to parse Python and Java source files. Extracts classes, functions, methods, imports, and function calls into structured models.

### `database`
SQLite-backed storage at `~/.codemind/codemind.db`. Two responsibilities:
- **Code index** — repositories, source files, symbols, imports, function calls
- **Analytics** — every API request recorded with IP, endpoint, method, status code, duration

Schema initializes automatically on first use via `initialize_database()`.

### `vectorstore`
ChromaDB-backed vector store at `~/.codemind/chroma/`. Stores code chunk embeddings with metadata (file path, symbol name, line range). Used by semantic and hybrid search.

### `embeddings`
Wraps `sentence-transformers` (`BAAI/bge-small-en-v1.5`) to generate normalized embeddings for code chunks and search queries.

### `chunking`
Splits parsed files into overlapping code chunks suitable for embedding and retrieval.

### `indexer`
Two indexers:
- **`RepositoryIndexer`** — scan + parse + save to SQLite
- **`SemanticIndexer`** — scan + parse + chunk + embed + save to ChromaDB

### `search`
Three strategies:
- **Keyword** (`CodeSearchService`) — SQLite `LIKE` query on symbol names
- **Semantic** (`SemanticSearchService`) — ChromaDB cosine similarity
- **Hybrid** (`HybridSearchService`) — combines both with Reciprocal Rank Fusion (RRF)

### `agent`
LangGraph state machine with four nodes:
- `select_tool` — LLM selects which tool to call next, receives observation history from prior steps
- `execute_tool` — runs the tool through guardrail validation
- `record_observation` — sanitizes and stores tool output in agent state
- `generate_answer` — LLM generates a grounded answer from all observations

Available tools: `search_symbols`, `find_symbol`, `get_source`, `analyze_change`.

### `graph`
NetworkX directed dependency graph. Resolves Python and Java imports to build file-level dependency edges. Used by `analyze_change` to find all files transitively affected by a change.

### `rag`
Builds structured prompts from retrieved code context. Enforces grounding — the LLM must cite sources and cannot invent implementation details.

### `llm`
HTTP client for the OpenRouter API (`httpx`). Supports standard chat completion and tool-calling. Default model: `openai/gpt-4o-mini`. Timeout: 60 seconds per call.

### `telemetry`
Anonymous usage tracking via **PostHog**.
- Fires a `codemind_ask` event on every `ask` command
- Payload: anonymous install ID, success/failure, iterations, query length, OS, Python version
- **No query text or file contents are ever sent**
- Project token is baked in — users do not configure this
- Opt out: set `CODEMIND_TELEMETRY=off` in `.env`
- PostHog project: US Cloud, project ID 707212

### `api`
FastAPI application deployed on **Render** at `https://codemind-cl2m.onrender.com`.
- `AnalyticsMiddleware` — records every request automatically
- `GET /health` — health check
- `POST /api/v1/repositories/scan` — scan a repository
- `GET /api/v1/analytics` — returns usage stats (total requests, unique clients, daily breakdown)

The `codemind info` CLI command calls this endpoint to show a real-time global user count.

## Deployment

The API runs on Render (free tier). Auto-deploys on every push to `main`. SQLite and ChromaDB are on ephemeral disk — analytics reset on redeploy. For persistent analytics, a hosted PostgreSQL database would be needed.

## Security

- **Path traversal prevention** — all file paths resolved and checked against repository root
- **Prompt injection detection** — tool outputs scanned for injection patterns before LLM use
- **Secret redaction** — API keys and tokens in tool outputs are redacted
- **Input validation** — all tool inputs validated by `GuardrailService` before execution
- **Telemetry opt-out** — users can disable with `CODEMIND_TELEMETRY=off`
