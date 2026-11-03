# CLI Reference

The installed command set is authoritative. Run:

```cmd
codemind --help
codemind <command> --help
```

## General

```cmd
codemind version
codemind info
```

`info` prints product/technology information and attempts to fetch the aggregate unique-client count from the hosted analytics endpoint. `unavailable` means that the count could not be retrieved; it does not prove local CLI functionality is broken.

## Repository scan

```cmd
codemind scan "C:\projects\sample-app"
```

Scans a repository directory and reports file inventory, directory/file totals, size, and language distribution.

## Structural index

```cmd
codemind index "C:\projects\sample-app"
```

Parses supported source files and stores repository, file, symbol, import, and call metadata in SQLite.

## Keyword search

```cmd
codemind search "PaymentService"
```

Searches the structural symbol index. Search scope and optional filters depend on the installed CLI options.

## Semantic index

```cmd
codemind semantic-index "C:\projects\sample-app"
```

Builds the vector index from supported symbol chunks. The documented supported semantic indexing extensions are Python and Java.

## Semantic search

```cmd
codemind semantic-search "where is payment validation implemented?"
```

Finds semantically related code chunks through embeddings and ChromaDB.

## Hybrid search

```cmd
codemind hybrid-search "payment validation"
```

Combines keyword and semantic rankings using Reciprocal Rank Fusion.

## Agent question

```cmd
codemind ask "Explain the payment flow" --repository "C:\projects\sample-app"
```

Runs the LangGraph agent against the selected repository and uses the configured OpenRouter model to generate an answer from tool observations.

## Retrieval benchmarks

The project includes retrieval evaluation utilities and benchmark commands. Inspect the installed CLI for exact arguments:

```cmd
codemind benchmark --help
codemind benchmark-dataset --help
```

## Recommended sequence

```cmd
codemind scan "C:\projects\sample-app"
codemind index "C:\projects\sample-app"
codemind semantic-index "C:\projects\sample-app"
codemind search "PaymentService"
codemind semantic-search "payment validation"
codemind hybrid-search "payment validation"
codemind ask "Explain the payment flow" --repository "C:\projects\sample-app"
```

## Local API

```cmd
uvicorn codemind.api.main:app --reload
```

See [API Reference](api-reference.md).
