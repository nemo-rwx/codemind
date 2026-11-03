# Frequently Asked Questions

## Does CodeMind upload my entire repository?

Repository scanning and indexing are local CLI workflows. However, when you use an LLM-powered feature, the application may send retrieved source excerpts and prompt context to OpenRouter. The optional PostHog `codemind_ask` event does not include raw query text or source-code content in the current implementation.

## Does Render store my local code index?

No. The hosted Render service runs the FastAPI backend. It does not automatically access the SQLite database, ChromaDB collection, or source files on a developer's laptop.

## Why does `codemind info` show `Total users: unavailable`?

The CLI could not retrieve a usable analytics response from the hosted API. Check the deployed endpoint and Render logs. Local code intelligence commands can still work independently.

## Which programming languages are supported?

The scanner recognizes a wider range of file types for inventory. The documented Tree-sitter parser and semantic indexing targets are Python and Java.

## What is the difference between keyword and semantic search?

Keyword search looks up indexed symbols by name. Semantic search compares vector embeddings of the query and code chunks. Hybrid search combines both rankings.

## Does the agent modify my source code?

The documented repository toolset is read-oriented. Do not assume the agent can edit files or execute arbitrary commands.

## Do I need OpenRouter?

OpenRouter is required for the LLM-powered workflows that use the configured OpenRouter client. Local scanning, parsing, and indexing do not inherently require an LLM request.

## Can I disable telemetry?

Yes. Set `CODEMIND_TELEMETRY=off` in the environment.

## Where can I inspect the API schema?

For a local API, open `http://127.0.0.1:8000/docs`. For the deployed service, open `https://codemind-cl2m.onrender.com/docs`.
