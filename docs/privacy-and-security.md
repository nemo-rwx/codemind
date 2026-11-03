# Privacy and Security

## Data-flow summary

CodeMind has multiple data flows that should be considered separately.

| Flow | Data involved | Destination |
|---|---|---|
| Local indexing | Repository source and extracted metadata | Local SQLite / ChromaDB |
| LLM request | Prompt plus context selected by the application | OpenRouter and configured model provider |
| CLI telemetry | Anonymous install ID and usage properties | PostHog |
| Hosted API request analytics | Request metadata such as endpoint, method, status, duration, and client IP | API analytics storage |

## Local repository data

Repository scanning, structural indexing, semantic indexing, and local agent tool execution are initiated by the CLI on the developer's machine. SQLite and ChromaDB hold local index data.

The hosted Render service does not automatically receive the user's local source tree or local index.

## LLM provider disclosure

When using an LLM-powered feature, CodeMind sends the messages and retrieved context assembled for the request to OpenRouter. This may include source-code excerpts returned by repository tools.

Do not use the tool with confidential or regulated code unless the provider configuration and your organization's policies permit that processing.

## PostHog telemetry

The current `codemind_ask` event records:
- Anonymous installation identifier
- Success/failure flag
- Agent iteration count
- Query character length
- Error summary, if present
- Python version
- Operating system

The event implementation does not include the raw natural-language query or source-code contents.

Disable it with:

```dotenv
CODEMIND_TELEMETRY=off
```

The stable anonymous install identifier is stored locally under the user's home directory in `.codemind/install_id`.

## API analytics

The FastAPI analytics middleware records request metadata including client IP, endpoint, method, status code, duration, and error detail. This API analytics flow is distinct from the PostHog CLI event.

Review retention, access, and persistence settings for the deployed analytics store before publishing a formal privacy policy.

## Security controls

The agent implementation includes:
- Tool allowlisting
- Input validation
- Repository path boundary checks
- Bounded source retrieval
- Prompt-injection pattern scanning
- Likely-secret redaction
- Output validation

These controls are defense-in-depth. They do not guarantee that every secret, injection attempt, or unsafe output will be detected.

## Credential handling

- Store OpenRouter keys in environment variables.
- Do not hardcode credentials.
- Rotate any credential that was accidentally committed or exposed.
- Keep `.env` and local data directories out of version control.

## Responsible use

Review AI-generated answers and retrieved source evidence before making code changes, deploying changes, or relying on security-related conclusions.
