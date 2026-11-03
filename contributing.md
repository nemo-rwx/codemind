# Contributing to CodeMind

Thank you for considering a contribution.

## Development setup

Windows CMD:

```cmd
git clone https://github.com/nemo-rwx/codemind.git
cd codemind
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -e ".[dev]"
```

Configure `.env` only when a test or workflow requires external services.

## Tests and quality

```cmd
python -m pytest
ruff check .
ruff format --check .
```

Add tests for behavior changes, including invalid input and failure cases.

## Contribution principles

- Keep local repository data and credentials out of Git.
- Preserve repository path boundaries in agent tools.
- Treat retrieved source and tool output as untrusted input.
- Keep external network calls out of unit tests where possible; mock provider clients.
- Document user-visible behavior and limitations.
- Avoid claiming support for a language unless parser/indexer behavior is implemented and tested.

## Pull request checklist

- [ ] Tests added or updated.
- [ ] Full test suite passes.
- [ ] Ruff checks pass.
- [ ] Documentation updated.
- [ ] No secrets, local indexes, or private repository contents included.
- [ ] Breaking changes and migration notes documented.
