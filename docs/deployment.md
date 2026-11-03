# Deployment

## Deployment model

The FastAPI backend is deployed to Render. The hosted base URL configured in the CLI is:

`https://codemind-cl2m.onrender.com`

The repository's `render.yaml` is the source of truth for service settings. Review it before changing build commands, start commands, environment variables, or health checks.

## Expected service configuration

The current project deployment configuration is intended to:
- Install the Python project
- Start Uvicorn bound to `0.0.0.0` and the Render-provided `$PORT`
- Use `/health` as the health-check path
- Configure OpenRouter credentials through Render environment settings

Confirm the exact values in the checked-in `render.yaml` and Render dashboard; do not rely on copied documentation if the deployment file has changed.

## Deploying updates

1. Commit and push the intended changes to the branch connected to the Render service.
2. Open the Render dashboard and select the CodeMind web service.
3. Inspect the deployment event and build logs.
4. Confirm required environment variables are configured.
5. Wait for the deployment to become live.
6. Verify the endpoints.

```cmd
curl -i https://codemind-cl2m.onrender.com/health
curl -i https://codemind-cl2m.onrender.com/api/v1/analytics
```

## Troubleshooting deployment

### Health endpoint fails

- Inspect Render deploy and runtime logs.
- Confirm the Uvicorn start command.
- Confirm the app binds to `0.0.0.0` and `$PORT`.
- Confirm the health-check path matches the API route.

### Analytics reports unavailable

The CLI `info` command displays `unavailable` when it cannot obtain a successful usable analytics response. Check the endpoint directly and inspect Render logs.

### Persistence

Do not assume local files written by the hosted service survive restarts or redeployments. Verify the Render disk/database configuration before relying on durable analytics persistence.

## Local vs hosted data

Render hosts the FastAPI process. It does not automatically host each CLI user's local SQLite database, ChromaDB collection, or source repository. The API scan endpoint can only scan paths accessible to the server process.
