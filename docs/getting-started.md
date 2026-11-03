# Getting Started

This guide walks through a first local setup and repository analysis.

## Prerequisites

- Python 3.11 or newer
- Git
- An OpenRouter API key for LLM-powered agent requests
- Network access for package installation, initial embedding-model download, and LLM requests

## 1. Get the source

```cmd
git clone https://github.com/nemo-rwx/codemind.git
cd codemind
```

## 2. Create a virtual environment

Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install

```cmd
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## 4. Configure the LLM provider

If the repository contains `.env.example`, copy it:

```cmd
copy .env.example .env
```

Set the required OpenRouter key in `.env`:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4o-mini
```

Use the model identifier configured for your account and project. Never commit `.env`.

## 5. Verify

```cmd
codemind --help
codemind version
codemind info
```

## 6. Analyze a repository

Use a repository path that exists on your own machine:

```cmd
codemind scan "C:\projects\sample-app"
codemind index "C:\projects\sample-app"
codemind semantic-index "C:\projects\sample-app"
```

The first semantic-index operation may download the Sentence Transformers model.

## 7. Search and ask

```cmd
codemind search "PaymentService"
codemind semantic-search "where is payment validation implemented?"
codemind hybrid-search "payment validation"
codemind ask "Explain the payment flow" --repository "C:\projects\sample-app"
```

Check `codemind <command> --help` for exact options supported by the installed version.

## 8. Run the API locally

```cmd
uvicorn codemind.api.main:app --reload
```

Then open `http://127.0.0.1:8000/docs`.

## Next

Read [Architecture](architecture.md) to understand the system boundaries and [Privacy and Security](privacy-and-security.md) before indexing sensitive repositories.
