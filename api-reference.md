# API Reference

Start the server:
```bash
uvicorn codemind.api.main:app --reload
```

Interactive docs: `http://localhost:8000/docs`

---

## Endpoints

### `GET /health`
Check whether the API is running.

**Response:**
```json
{ "status": "healthy", "service": "CodeMind API" }
```

---

### `POST /api/v1/repositories/scan`
Scan a repository and return file metadata.

**Request body:**
```json
{ "path": "C:/projects/my-repo" }
```

**Response:**
```json
{
  "root_path": "C:/projects/my-repo",
  "total_files": 42,
  "total_directories": 8,
  "total_size_bytes": 102400,
  "language_counts": { "Python": 40, "Other": 2 },
  "files": [
    { "path": "src/main.py", "extension": ".py", "language": "Python", "size_bytes": 1024 }
  ],
  "errors": []
}
```

**Error responses:**
- `404` — path does not exist
- `400` — path is not a directory

---

### `GET /api/v1/analytics`
Return API usage statistics.

**Response:**
```json
{
  "total_requests": 142,
  "unique_clients": 5,
  "error_requests": 3,
  "avg_duration_ms": 12.4,
  "requests_by_endpoint": [
    { "endpoint": "/api/v1/repositories/scan", "requests": 98 }
  ],
  "requests_per_day": [
    { "date": "2026-11-03", "requests": 42 }
  ],
  "top_queries": []
}
```
