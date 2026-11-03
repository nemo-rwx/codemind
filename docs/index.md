# CodeMind Documentation

Welcome to the CodeMind technical documentation.

CodeMind is a local-first codebase intelligence CLI that combines repository scanning, Tree-sitter parsing, structured metadata storage, semantic retrieval, hybrid search, dependency analysis, and an LLM-powered agent workflow.

## Documentation map

| Guide | What it covers |
|---|---|
| [Getting started](getting-started.md) | First-time setup and first repository workflow |
| [Installation](installation.md) | Supported setup steps and environment configuration |
| [Architecture](architecture.md) | Components, data flow, and system boundaries |
| [CLI reference](cli-reference.md) | CLI commands and usage examples |
| [Indexing](indexing.md) | Scanning, parsing, structural and semantic indexing |
| [Search and retrieval](search-and-retrieval.md) | Keyword, semantic, hybrid search, and evaluation |
| [Agent workflow](agent-workflow.md) | LangGraph orchestration, tools, RAG, and guardrails |
| [API reference](api-reference.md) | FastAPI endpoints |
| [Deployment](deployment.md) | Render deployment and operational checks |
| [Configuration](configuration.md) | Environment variables and runtime configuration |
| [Privacy and security](privacy-and-security.md) | Data flows, telemetry, and security controls |
| [Troubleshooting](troubleshooting.md) | Common installation and runtime issues |
| [FAQ](faq.md) | Frequently asked questions |

## Product boundaries

The documented Tree-sitter parser and semantic indexing targets are Python and Java. The scanner can identify additional file types for inventory purposes; language detection alone does not imply parser or semantic-index support.

Repository scanning, indexing, retrieval, and agent workflows are initiated locally through the CLI. The hosted Render service runs the FastAPI application and its API endpoints. It does not automatically mount a developer's local repository or local index.

For exact command options and deployed API schemas, inspect the installed CLI help and the live OpenAPI documentation.
