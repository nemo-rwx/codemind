# CodeMind CLI

A Python-first codebase intelligence CLI. This starter includes the initial repository scanner.

## Requirements

- Python 3.11+

## Setup

### Create and activate a virtual environment

macOS/Linux:
```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:
```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
```

### Install

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Try it

```bash
codemind --help
codemind version
codemind info
codemind scan .
```

## Run tests

```bash
pytest -v
```

## Current scope

The scanner discovers files, skips common generated/dependency directories, identifies languages by file extension, and reports basic repository statistics. It does not yet parse code semantics or fully implement `.gitignore` rules.
