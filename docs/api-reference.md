# API Reference

## Run locally

```cmd
uvicorn codemind.api.main:app --reload
```

Base URL: `http://127.0.0.1:8000`

Interactive API schema: `http://127.0.0.1:8000/docs`

## Hosted base URL

`https://codemind-cl2m.onrender.com`

## `GET /health`

Health endpoint for checking whether the FastAPI application is responding.

```cmd
curl -i https://codemind-cl2m.onrender.com/health
```

Use the deployed OpenAPI schema to confirm the exact response body.

## `POST /api/v1/repositories/scan`

Scans a directory path visible to the API process.

Request model:

```json
{
  "path": "C:/path/visible/to/the/api-process"
}
```

Example:

```cmd
curl -X POST https://codemind-cl2m.onrender.com/api/v1/repositories/scan -H "Content-Type: application/json" -d "{\"path\":\"/path/visible/to/api\"}"
```

The path is resolved on the server running FastAPI. Sending a path from the caller's laptop does not make that local directory available to the hosted service.

The route documents:
- `404` when the path is not found
- `400` when the path is not a directory

The successful response uses the repository summary schema defined by the application.

## `GET /api/v1/analytics`

Returns aggregate API analytics used by the CLI `info` command.

```cmd
curl -i https://codemind-cl2m.onrender.com/api/v1/analytics
```

The CLI reads the `unique_clients` field when the endpoint returns a successful response.

## Deployed schema is authoritative

For exact request/response models and any future route changes, use:

`https://codemind-cl2m.onrender.com/docs`

Do not treat example paths as paths that necessarily exist in the hosted container.
