# CodeMind

Agentic AI-powered codebase intelligence — ask questions about any repository in plain English.

```
codemind ask "How does authentication work?" --repository ./my-project
```

## Features

- **Ask questions** about any Python or Java codebase in natural language
- **Semantic search** — find code by meaning, not just symbol names
- **Hybrid search** — combines keyword and semantic retrieval with RRF ranking
- **Change impact analysis** — find files affected by changing a source file
- **REST API** — integrate CodeMind into your own tools
- **Usage analytics** — track API usage over time

## Quick Start

### Requirements

- Python 3.11+
- An [OpenRouter](https://openrouter.ai) API key (free tier available)

### Install

```powershell
git clone https://github.com/nemo-rwx/codemind.git
cd codemind
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### Configure

```powershell
copy .env.example .env
```

Edit `.env` and add your OpenRouter key:

```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini
```

Get a free key at [openrouter.ai](https://openrouter.ai).

### Use it

```powershell
# Index your repository first
codemind index C:\path\to\your\repo

# Ask a question
codemind ask "What does the scanner do?" --repository C:\path\to\your\repo

# Search for a symbol
codemind search "CodeMindAgent"
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [CLI Reference](docs/cli-reference.md)
- [API Reference](docs/api-reference.md)
- [Architecture](docs/architecture.md)
- [Contributing](docs/contributing.md)

## Telemetry

CodeMind sends anonymous usage events when you run `ask` to help the maintainer understand how the tool is being used. This requires no setup on your part — there is no key to configure.

What is collected: which command ran, success or failure, number of agent iterations, query length, OS, Python version. **No query text, file contents, or personal data is ever sent.**

To opt out, add this to your `.env`:

```
CODEMIND_TELEMETRY=off
```

## License

MIT
