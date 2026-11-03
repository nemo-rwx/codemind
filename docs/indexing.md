# Repository Indexing

CodeMind maintains a structural metadata index and a semantic vector index. They serve different retrieval needs.

## Repository scanning

The scanner walks the selected directory, applies ignore rules for common generated or environment folders, and records file metadata such as relative path, extension, detected language, and file size.

Language detection is an inventory feature. A detected language does not necessarily have a parser or semantic indexer implementation.

## Supported parsing targets

The documented Tree-sitter parser targets are:
- Python
- Java

The parser extracts:
- Class and interface-like declarations supported by the grammar logic
- Functions, methods, and constructors where implemented
- Import statements
- Function/method call names
- Source line ranges
- Parse errors

Extraction quality depends on the parser implementation and grammar node handling. It is not a complete semantic compiler.

## Structural index

Run:

```cmd
codemind index "C:\projects\sample-app"
```

The structural index stores:
- Repositories
- Source files
- Symbols
- Imports
- Calls

SQLite provides relational metadata and indexed symbol lookups. Re-indexing a source file updates its metadata and replaces its extracted symbol/import/call rows.

## Semantic index

Run:

```cmd
codemind semantic-index "C:\projects\sample-app"
```

The semantic indexing pipeline:
1. Scans the repository.
2. Selects supported parser extensions.
3. Parses files.
4. Extracts symbol-level code chunks.
5. Generates embeddings using `BAAI/bge-small-en-v1.5`.
6. Upserts chunk documents into ChromaDB.
7. Removes stale vector documents after a successful complete indexing pass.

The embedding model may be downloaded the first time it is initialized.

## Storage responsibilities

| Store | Stores | Used for |
|---|---|---|
| SQLite | Repository/file/symbol/import/call records | Structured lookups and keyword search |
| ChromaDB | Chunk text, embeddings, and metadata | Semantic vector retrieval |
| NetworkX (runtime graph) | Dependency relationships | Dependency and change-impact analysis |

## Re-indexing guidance

Re-run structural and semantic indexing after meaningful source changes. If a semantic index is incomplete because files failed to parse or index, review the reported errors before relying on the results.

## Operational cautions

- Do not index virtual environments, build outputs, generated files, or large vendor directories unless explicitly intended.
- Keep the local database and vector-store directories out of Git.
- Back up local index data only if you need to preserve it; it can generally be regenerated from source repositories.
