# Configuration

## Environment variables

The application uses environment configuration for external service credentials and optional telemetry control.

| Variable | Purpose |
|---|---|
| `OPENROUTER_API_KEY` | Credential for OpenRouter requests |
| `OPENROUTER_MODEL` | Model identifier used by the LLM client/configuration |
| `CODEMIND_TELEMETRY` | Enables/disables the CLI PostHog event |

Example local `.env`:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4o-mini
CODEMIND_TELEMETRY=on
```

The exact default model should be checked in the current source/configuration before changing deployment documentation.

## Telemetry switch

Telemetry is enabled unless `CODEMIND_TELEMETRY` is one of:
- `off`
- `0`
- `false`

Values are compared case-insensitively.

Disable telemetry:

```dotenv
CODEMIND_TELEMETRY=off
```

## Local configuration

Create a local `.env` from `.env.example` if that file is present:

```cmd
copy .env.example .env
```

Never commit `.env`, API keys, tokens, or credentials.

## Render configuration

Set server-side secrets through the Render dashboard or supported secret configuration. Do not commit production credentials in `render.yaml`.

## Storage

SQLite and ChromaDB are used for local repository metadata and vector retrieval. Consult `codemind/database` and `codemind/vectorstore` for the exact paths and persistence settings in the installed version.
