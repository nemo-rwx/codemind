# Getting Started

## Prerequisites

- Python 3.11 or higher
- Git
- An OpenRouter API key — sign up free at [openrouter.ai](https://openrouter.ai)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/nemo-rwx/codemind.git
cd codemind
```

### 2. Create a virtual environment

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

### 4. Configure your API key

```bash
cp .env.example .env   # macOS/Linux
copy .env.example .env  # Windows
```

Open `.env` and fill in your key:

```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini
```

## First use

### Index a repository

Before you can ask questions, CodeMind needs to index the repository:

```bash
codemind index /path/to/your/repo
```

This parses all Python and Java files, extracts symbols, and builds a searchable index.

### Ask a question

```bash
codemind ask "How does the authentication system work?" --repository /path/to/your/repo
```

The agent will investigate the codebase using up to 5 tool calls and return a grounded answer with source references.

### Search for symbols

```bash
codemind search "PaymentService"
```

### Scan a repository

```bash
codemind scan /path/to/your/repo
```

Returns file counts, language distribution, and total size.

## Opt out of telemetry

CodeMind sends anonymous usage events to help improve the tool. To disable:

```
CODEMIND_TELEMETRY=off
```

Add this to your `.env` file.
