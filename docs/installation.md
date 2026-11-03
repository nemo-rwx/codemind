# Installation

## Supported runtime

The project has been developed and tested with Python 3.11. Use the Python version declared in `pyproject.toml` as the authoritative requirement if it changes.

## Windows CMD

```cmd
git clone https://github.com/nemo-rwx/codemind.git
cd codemind
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## PowerShell

```powershell
git clone https://github.com/nemo-rwx/codemind.git
cd codemind
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## macOS / Linux

```bash
git clone https://github.com/nemo-rwx/codemind.git
cd codemind
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Environment file

If `.env.example` is present:

```cmd
copy .env.example .env
```

Configure the OpenRouter key:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4o-mini
CODEMIND_TELEMETRY=on
```

The telemetry setting is optional. Set it to `off`, `0`, or `false` to disable the CLI PostHog event.

## Verify installation

```cmd
codemind --help
codemind version
python -m pytest
```

## Editable installation

`pip install -e ".[dev]"` installs the project in editable mode with development dependencies. After changing package code, rerun tests; reinstall only when project metadata or dependencies change.

## Troubleshooting

If the `codemind` command is not found:
1. Confirm the virtual environment is activated.
2. Confirm the terminal is at the repository root.
3. Run `python -m pip install -e ".[dev]"`.
4. Verify with `python -m codemind.cli.main --help` if the package module is importable.
