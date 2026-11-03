# Search and Retrieval

CodeMind provides three retrieval modes.

## Keyword search

Keyword search uses the SQLite structural index to locate symbols by name. It is useful when the developer knows a class, method, or function identifier.

Example:

```cmd
codemind search "PaymentService"
```

Keyword search depends on the repository having been structurally indexed first.

## Semantic search

Semantic search embeds a natural-language query and compares it with stored code-chunk embeddings in ChromaDB.

Example:

```cmd
codemind semantic-search "where is the payment amount validated?"
```

The semantic index must exist before useful results can be returned. The query embedding uses a retrieval-oriented prefix in the current embedding service.

## Hybrid search

Hybrid search combines keyword and semantic result rankings. The current implementation uses Reciprocal Rank Fusion (RRF), with a rank constant of 60.

Conceptually:

```text
RRF(document) = sum(1 / (60 + rank))
```

A document returned by both retrieval methods can receive a stronger combined score than a document found by only one method.

Example:

```cmd
codemind hybrid-search "payment validation"
```

## Retrieval metadata

Semantic chunks retain metadata such as:
- Repository identity/path
- Relative file path
- Symbol name
- Symbol kind
- Start and end lines
- Language

Keyword results include symbol and source-location metadata. Hybrid result fields can differ depending on which retrieval sources contributed.

## Evaluation

The project contains retrieval metrics including:
- Precision at K
- Recall at K
- Reciprocal rank
- Mean reciprocal rank

Benchmark evaluation compares retrieved document identifiers against relevant identifiers supplied in a benchmark dataset.

A retrieval score is meaningful only when the dataset's relevance labels and document-ID mapping are correct. Do not compare scores across datasets without checking their query and relevance distributions.
