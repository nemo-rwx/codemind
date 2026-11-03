# CodeMind

### Agentic AI-Powered Codebase Intelligence

**Understand your codebase. Explore dependencies. Investigate code. Ask questions in natural language.**

CodeMind is an AI-powered codebase intelligence CLI designed to help developers understand, navigate, and investigate software repositories through structural code analysis, semantic retrieval, hybrid search, dependency analysis, and agentic AI workflows.

Instead of manually navigating hundreds of files, developers can ask questions about their codebase and retrieve relevant implementation context through an AI-assisted investigation workflow.

---

## Overview

Modern software repositories are complex. Understanding an unfamiliar project often requires navigating multiple modules, tracing dependencies, identifying implementation details, and connecting information across files.

CodeMind combines traditional code analysis with modern AI retrieval techniques to simplify this process.

It provides:

- Repository scanning and language detection
- Tree-sitter-based source code parsing
- Symbol, import, and function-call extraction
- SQLite-powered metadata storage
- Semantic code search using embeddings
- ChromaDB vector storage
- Hybrid retrieval using Reciprocal Rank Fusion
- Dependency graph analysis using NetworkX
- Retrieval-Augmented Generation (RAG)
- LangGraph-based agent orchestration
- OpenRouter-powered LLM integration
- FastAPI backend and hosted analytics
- Optional PostHog usage telemetry

## Key Features

### Repository Intelligence

Scan software repositories and extract structural information, including files, languages, symbols, imports, and function calls.

### Code Parsing

Use Tree-sitter to analyze supported source files and extract:

- Classes
- Functions and methods
- Imports
- Function calls
- Source locations
- Parsing errors

The currently documented parser targets are Python and Java.

### Semantic Search

Find relevant code using natural-language queries instead of relying exclusively on exact symbol names.

CodeMind uses `BAAI/bge-small-en-v1.5` to generate embeddings and ChromaDB to perform vector retrieval.

### Hybrid Search

Combine keyword-based and semantic retrieval using Reciprocal Rank Fusion (RRF).

This helps retrieve relevant code even when the user's terminology differs from the actual implementation.

### Agentic Investigation

CodeMind uses LangGraph to orchestrate an investigation workflow.

The agent can select repository tools, execute validated operations, record observations, and generate an answer using the retrieved evidence.

### Dependency and Change Impact Analysis

Use NetworkX to represent dependency relationships and identify potentially affected files when a source file changes.

### RAG-Based Answers

Retrieved source code is assembled into bounded context and passed to the configured LLM through OpenRouter.

The system is designed to produce repository-grounded answers rather than relying exclusively on general model knowledge.

---

## Architecture

```text
                  DEVELOPER
                      |
                      v
               CODEMIND CLI
                Typer + Rich
                      |
          +-----------+-----------+
          |                       |
          v                       v
   REPOSITORY SCANNER        AGENT WORKFLOW
          |                    LangGraph
          v                       |
     TREE-SITTER                  v
       PARSER                TOOL EXECUTOR
          |                       |
          v                       v
       SQLITE              REPOSITORY TOOLS
    METADATA INDEX                |
          |                       v
          |                  OBSERVATIONS
          |                       |
          v                       v
    CODE CHUNKING             RAG CONTEXT
          |                       |
          v                       v
   EMBEDDING MODEL            OPENROUTER
          |                       |
          v                       v
       CHROMADB              AI RESPONSE
          |
          v
    SEMANTIC SEARCH
          |
          v
      HYBRID SEARCH
```

### Hosted Infrastructure

```text
          CODEMIND CLI
                |
                | HTTPS
                v
          RENDER CLOUD
                |
                v
          FASTAPI BACKEND
                |
       +--------+---------+
       |                  |
       v                  v
   HEALTH API        ANALYTICS API

   CODEMIND CLI
       |
       v
    POSTHOG
       |
       v
   USAGE TELEMETRY
```

Render hosts the FastAPI backend. Local repository indexing and agent workflows are performed by the CLI on the developer's machine.

---

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| CLI | Typer, Rich |
| API | FastAPI |
| Validation | Pydantic |
| Parsing | Tree-sitter |
| Metadata storage | SQLite |
| Vector database | ChromaDB |
| Embeddings | Sentence Transformers |
| Embedding model | BAAI/bge-small-en-v1.5 |
| Dependency graph | NetworkX |
| Agent orchestration | LangGraph |
| LLM provider | OpenRouter |
| Retrieval architecture | RAG |
| Analytics | PostHog |
| Hosting | Render |
| Testing | Pytest |
| Code quality | Ruff |

---

## Installation

### Requirements

- Python 3.11+
- Git
- OpenRouter API key for LLM-powered workflows

### Clone the repository

```bash
git clone https://github.com/nemo-rwx/codemind.git
cd codemind
```

### Create a virtual environment

**Windows CMD**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Configure environment

Create a `.env` file using the provided example:

```bash
copy .env.example .env
```

Configure your OpenRouter credentials:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4o-mini
CODEMIND_TELEMETRY=on
```

Never commit API keys or credentials to version control.

---

## Quick Start

### 1. Verify installation

```bash
codemind --help
codemind version
codemind info
```

### 2. Scan a repository

```bash
codemind scan "C:\projects\my-project"
```

### 3. Build the structural index

```bash
codemind index "C:\projects\my-project"
```

### 4. Build the semantic index

```bash
codemind semantic-index "C:\projects\my-project"
```

### 5. Search the codebase

```bash
codemind search "PaymentService"
```

### 6. Perform semantic search

```bash
codemind semantic-search "Where is payment validation implemented?"
```

### 7. Perform hybrid search

```bash
codemind hybrid-search "payment validation"
```

### 8. Ask the AI agent

```bash
codemind ask "Explain the overall architecture of this project" --repository "C:\projects\my-project"
```

Use `codemind --help` to inspect the commands and options available in your installed version.

---

## Backend API

CodeMind provides a FastAPI backend.

**Hosted API:**

https://codemind-cl2m.onrender.com

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Service health check |
| `/api/v1/repositories/scan` | POST | Scan a server-accessible repository path |
| `/api/v1/analytics` | GET | Retrieve aggregate API analytics |
| `/docs` | GET | Interactive API documentation |

### Run locally

```bash
uvicorn codemind.api.main:app --reload
```

Local API documentation:

http://127.0.0.1:8000/docs

**Note:** A repository path sent to the hosted scan endpoint must exist in the server's filesystem. It does not automatically refer to a directory on the developer's laptop.

---

## Analytics and Telemetry

CodeMind integrates PostHog for optional CLI usage telemetry.

The `codemind_ask` event records usage information such as:

- Anonymous installation identifier
- Operation success or failure
- Agent iteration count
- Query character length
- Python version
- Operating system
- Error summary, when available

The telemetry implementation does not send the natural-language query text or source-code contents in this event.

Disable telemetry:

```dotenv
CODEMIND_TELEMETRY=off
```

API request analytics are handled separately by the FastAPI backend.

---

## Security and Privacy

CodeMind includes several defensive controls:

- Repository path validation
- Restricted agent tool execution
- Bounded source-code retrieval
- Prompt-injection pattern detection
- Likely-secret redaction
- Output validation
- Optional telemetry opt-out

Repository indexing is designed to operate locally.

When an LLM request is made, the context assembled for that request is sent to the configured OpenRouter provider. Review your provider settings and data-handling requirements before using CodeMind with confidential source code.

These security controls are defense-in-depth measures, not a guarantee of complete protection.

---

## Project Structure

```text
codemind/
├── codemind/
│   ├── agent/
│   ├── api/
│   ├── chunking/
│   ├── cli/
│   ├── database/
│   ├── embeddings/
│   ├── graph/
│   ├── indexer/
│   ├── llm/
│   ├── parser/
│   ├── rag/
│   ├── scanner/
│   ├── search/
│   ├── vectorstore/
│   └── telemetry.py
│
├── benchmarks/
├── tests/
├── docs/
├── pyproject.toml
├── render.yaml
└── README.md
```

---

## Testing

Run the complete test suite:

```bash
python -m pytest
```

Run code-quality checks:

```bash
ruff check .
ruff format --check .
```

---

## Limitations

- Documented Tree-sitter parser support currently targets Python and Java.
- Semantic indexing is limited to the supported parser extensions.
- Dependency resolution is best-effort and is not a full compiler or build-system analysis.
- AI answers depend on retrieved evidence and the configured LLM.
- Hosted API availability and analytics persistence depend on the Render service configuration.

---

## Roadmap

Potential future improvements:

- Additional programming language parsers
- More advanced cross-language dependency resolution
- Improved symbol-level and file-level retrieval
- More detailed investigation evidence and citations
- Expanded agent evaluation and observability
- Improved API authentication and operational monitoring
- Package distribution and automated release workflows

---

## Contributing

Contributions, bug reports, feature requests, and suggestions are welcome.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Author

**CodeMind — Agentic AI-Powered Codebase Intelligence**

Built with Python, AI, and a little curiosity about how software works.

GitHub: https://github.com/nemo-rwx/codemind
