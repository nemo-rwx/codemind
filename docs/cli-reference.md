# CLI Reference

## Global options

```
codemind --help        Show help
codemind --version     Show version
```

---

## Commands

### `version`
Display the current CodeMind version.
```bash
codemind version
```

---

### `info`
Display project information and community stats.
```bash
codemind info
```

---

### `scan`
Scan a repository and report file statistics.
```bash
codemind scan <path>
```

**Arguments:**
- `path` — path to the repository directory

**Output:** file count, directory count, total size, language breakdown table.

---

### `index`
Parse and index a repository into the SQLite database.
```bash
codemind index <path>
```

**Arguments:**
- `path` — path to the repository directory

Must be run before `search` or `ask`. Supports Python and Java files.

---

### `search`
Search indexed symbols by name.
```bash
codemind search <query>
```

**Arguments:**
- `query` — class, method, or function name (partial match supported)

---

### `semantic-index`
Generate embeddings and index code into ChromaDB.
```bash
codemind semantic-index [path]
```

**Arguments:**
- `path` — repository path (default: current directory)

Run this in addition to `index` to enable semantic and hybrid search.

---

### `semantic-search`
Search code by semantic similarity.
```bash
codemind semantic-search <query> [--top-k N]
```

**Arguments:**
- `query` — natural language description of what you are looking for

**Options:**
- `--top-k N` — number of results to return (default: 5, max: 20)

---

### `hybrid-search`
Search using both keyword and semantic retrieval combined with RRF ranking.
```bash
codemind hybrid-search <query> [--top-k N]
```

---

### `ask`
Ask the CodeMind agent a question about a repository.
```bash
codemind ask <query> [--repository <path>] [--top-k N]
```

**Arguments:**
- `query` — your question in plain English

**Options:**
- `--repository` / `-r` — path to the repository (default: current directory)
- `--top-k N` — retrieval depth (default: 5)

**Example:**
```bash
codemind ask "How does the scanner handle symlinks?" --repository ./codemind
```

The agent runs up to 5 investigation steps using tools (`search_symbols`, `find_symbol`, `get_source`, `analyze_change`) before generating a grounded answer.

---

### `benchmark`
Benchmark retrieval strategies for a single query.
```bash
codemind benchmark <query> --relevant <id> [--relevant <id>...] [--repository <path>] [--top-k N]
```

---

### `benchmark-dataset`
Evaluate retrieval across a full benchmark dataset.
```bash
codemind benchmark-dataset <dataset.json>
```

The dataset JSON must have this structure:
```json
{
  "queries": [
    { "query": "find payment logic", "relevant": ["src/payments.py::PaymentService::42"] }
  ]
}
```
