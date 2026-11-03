# Troubleshooting

## `codemind` is not recognized

Activate the project's virtual environment and install the package in editable mode:

```cmd
.venv\Scripts\activate.bat
python -m pip install -e ".[dev]"
codemind --help
```

## `ModuleNotFoundError: No module named 'codemind'`

Run commands from the project root, where `pyproject.toml` and the `codemind` package directory are located:

```cmd
python -m pip install -e ".[dev]"
python -m codemind.cli.main --help
```

## OpenRouter request fails

Check:
- `OPENROUTER_API_KEY` is set and valid.
- The configured model identifier is available to your account.
- Network connectivity is working.
- Provider rate limits and account credits.
- Render environment variables, if the failing request originates from the hosted API.

Do not paste credentials into issue reports.

## Semantic indexing is slow on first run

The embedding model may need to download and initialize. Subsequent runs can reuse the local model cache.

## Semantic search returns no results

1. Run `codemind semantic-index <repository-path>`.
2. Confirm that the repository contains supported Python or Java source files.
3. Review indexing errors.
4. Search with a more specific natural-language query.
5. Confirm the repository filter/path matches the indexed repository.

## `Total users: unavailable`

The `info` command could not retrieve a usable response from the hosted analytics endpoint.

Check:

```cmd
curl -i https://codemind-cl2m.onrender.com/api/v1/analytics
```

Also inspect Render service logs. This issue does not necessarily affect local scanning, indexing, or search.

## Render health check fails

- Check the latest deployment logs.
- Confirm the Uvicorn command.
- Confirm the process binds to `0.0.0.0` and `$PORT`.
- Confirm `/health` is registered.
- Confirm environment variables required at startup.

## Ruff formatting check crashes

If Ruff itself crashes, capture:
- `ruff --version`
- Python version
- The exact command
- The relevant file and `pyproject.toml` lint configuration

Try updating the development dependency to a current compatible Ruff release, then rerun the check. Do not treat a Ruff crash as proof that the source passed formatting.

## Tests

Run the suite from the project root:

```cmd
python -m pytest
```

Run an individual test module:

```cmd
python -m pytest tests\test_parser.py -v
```

Use a test file that actually exists in your checkout.
