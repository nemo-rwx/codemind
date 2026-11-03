from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from codemind.agent.graph import CodeMindAgent
from codemind.telemetry import capture_ask
from codemind.database.schema import initialize_database
from codemind.indexer.semantic import SemanticIndexer
from codemind.indexer.service import RepositoryIndexer
from codemind.scanner.service import RepositoryScanner
from codemind.search.benchmark import RetrievalBenchmark
from codemind.search.hybrid import HybridSearchService
from codemind.search.semantic import SemanticSearchService
from codemind.search.service import CodeSearchService

app = typer.Typer(
    name="codemind",
    help="Agentic AI powered Codebase Intelligence CLI",
    no_args_is_help=True,
)

console = Console()


# --------------------------------------------------
# VERSION
# --------------------------------------------------


@app.command()
def version():
    """Display CodeMind version."""
    console.print("[bold green]CodeMind v0.1.0[/bold green]")


# --------------------------------------------------
# INFO
# --------------------------------------------------


def _get_total_users() -> str:
    """Count unique install IDs from local analytics database."""
    try:
        from codemind.database.analytics import AnalyticsRepository
        repo = AnalyticsRepository()
        summary = repo.summary()
        return str(summary["unique_clients"])
    except Exception:
        pass
    return "unavailable"



@app.command()
def info():
    """Display project information."""

    console.print("\n[bold cyan]CodeMind[/bold cyan]")
    console.print("Agentic AI powered Codebase Intelligence CLI")

    console.print("\n[bold]Technology Stack:[/bold]")
    console.print("- Python")
    console.print("- Typer and Rich")
    console.print("- FastAPI")
    console.print("- Tree-sitter")
    console.print("- SQLite")
    console.print("- ChromaDB")
    console.print("- NetworkX")
    console.print("- LangGraph")
    console.print("- OpenRouter")

    total_users = _get_total_users()
    console.print("\n[bold]Community:[/bold]")
    console.print(f"- Total users: {total_users}")


# --------------------------------------------------
# REPOSITORY SCAN
# --------------------------------------------------


@app.command()
def scan(
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Path to the repository to scan",
    ),
):
    """Scan a software repository."""

    try:
        scanner = RepositoryScanner()
        result = scanner.scan(path)

        console.print("\n[bold green]Repository Scan Completed![/bold green]")

        console.print(f"Repository: {result.root_path}")
        console.print(f"Total files: {result.total_files}")
        console.print(f"Total directories: {result.total_directories}")
        console.print(f"Total size: {result.total_size_bytes} bytes")

        table = Table(title="Language Distribution")
        table.add_column("Language", style="cyan")
        table.add_column("Files", justify="right")

        for language, count in result.language_counts.items():
            table.add_row(language, str(count))

        console.print(table)

    except (FileNotFoundError, NotADirectoryError, OSError) as error:
        console.print(f"[bold red]Error: {error}[/bold red]")
        raise typer.Exit(code=1) from error


# --------------------------------------------------
# REPOSITORY INDEX
# --------------------------------------------------


@app.command()
def index(
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Repository path to index",
    ),
):
    """Scan, parse, and index a repository."""

    initialize_database()
    try:
        indexer = RepositoryIndexer()
        result = indexer.index_repository(path)

        console.print("\n[bold green]Indexing Completed Successfully![/bold green]")

        table = Table(title="CodeMind Indexing Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for key, value in result.items():
            if key != "errors":
                table.add_row(key, str(value))

        console.print(table)

        if result.get("errors"):
            console.print("\n[yellow]Warnings / Errors:[/yellow]")

            for error in result["errors"]:
                console.print(f"- {error}")

    except Exception as error:
        console.print(f"[bold red]Indexing failed: {error}[/bold red]")
        raise typer.Exit(code=1) from error


# --------------------------------------------------
# KEYWORD SEARCH
# --------------------------------------------------


@app.command()
def search(
    query: str = typer.Argument(
        ...,
        help="Class, method, or function name to search",
    ),
):
    """Search indexed code symbols."""

    initialize_database()
    try:
        search_service = CodeSearchService()
        results = search_service.search(query)

        if not results:
            console.print(f"[yellow]No symbols found for: {query}[/yellow]")
            return

        table = Table(title=f"Code Search Results: {query}")

        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Language")
        table.add_column("File")
        table.add_column("Start Line", justify="right")
        table.add_column("End Line", justify="right")

        for result in results:
            table.add_row(
                result["name"],
                result["kind"],
                result["language"],
                result["file_path"],
                str(result["start_line"]),
                str(result["end_line"]),
            )

        console.print(table)
        console.print(f"\nFound {len(results)} matching symbols.")

    except ValueError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error


# --------------------------------------------------
# SEMANTIC INDEX
# --------------------------------------------------


@app.command("semantic-index")
def semantic_index(
    path: str = typer.Argument(
        ".",
        help="Repository path to semantically index",
    ),
):
    """Generate embeddings and index repository code in ChromaDB."""

    try:
        indexer = SemanticIndexer()

        console.print("[cyan]Starting semantic repository indexing...[/cyan]")

        result = indexer.index_repository(Path(path))

        table = Table(title="Semantic Indexing Results")

        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Repository", result["repository"])
        table.add_row("Total files", str(result["total_files"]))
        table.add_row("Indexed files", str(result["indexed_files"]))
        table.add_row("Skipped files", str(result["skipped_files"]))
        table.add_row("Failed files", str(result["failed_files"]))
        table.add_row("Indexed chunks", str(result["indexed_chunks"]))

        console.print(table)

        if result["errors"]:
            console.print("[yellow]Indexing errors:[/yellow]")

            for error in result["errors"]:
                console.print(f"[yellow]- {error}[/yellow]")

    except Exception as error:
        console.print(f"[red]Semantic indexing failed: {error}[/red]")
        raise typer.Exit(code=1) from error


# --------------------------------------------------
# SEMANTIC SEARCH
# --------------------------------------------------


@app.command("semantic-search")
def semantic_search(
    query: str = typer.Argument(
        ...,
        help="Natural-language question about the codebase",
    ),
    top_k: int = typer.Option(
        5,
        "--top-k",
        "-k",
        min=1,
        max=20,
        help="Number of matching code chunks to retrieve",
    ),
):
    """Search code using semantic similarity."""

    try:
        service = SemanticSearchService()

        console.print(f"\n[cyan]Searching codebase for:[/cyan] {query}\n")

        results = service.search(query, top_k=top_k)

        if not results:
            console.print(
                "[yellow]No indexed code chunks found. "
                "Run semantic-index first.[/yellow]"
            )
            return

        table = Table(title="Semantic Search Results")

        table.add_column("Rank", justify="right")
        table.add_column("Symbol", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("File")
        table.add_column("Lines", justify="center")
        table.add_column("Distance", justify="right")

        for index, result in enumerate(results, start=1):
            metadata = result["metadata"]

            table.add_row(
                str(index),
                metadata.get("symbol", "Unknown"),
                metadata.get("kind", "Unknown"),
                metadata.get("file_path", "Unknown"),
                (f"{metadata.get('start_line', '?')}-{metadata.get('end_line', '?')}"),
                f"{result['distance']:.4f}",
            )

        console.print(table)

        console.print("\n[bold]Retrieved code snippets:[/bold]")

        for index, result in enumerate(results, start=1):
            metadata = result["metadata"]

            console.print(
                f"\n[cyan]Result {index}: {metadata.get('symbol', 'Unknown')}[/cyan]"
            )

            console.print(
                f"[dim]{metadata.get('file_path', 'Unknown')} "
                f"(lines {metadata.get('start_line', '?')}-"
                f"{metadata.get('end_line', '?')})[/dim]"
            )

            console.print(result["text"])

    except ValueError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    except Exception as error:
        console.print(f"[red]Semantic search failed: {error}[/red]")
        raise typer.Exit(code=1) from error


# --------------------------------------------------
# HYBRID SEARCH
# --------------------------------------------------


@app.command("hybrid-search")
def hybrid_search(
    query: str = typer.Argument(
        ...,
        help="Search query for keyword and semantic retrieval",
    ),
    top_k: int = typer.Option(
        5,
        "--top-k",
        "-k",
        min=1,
        max=20,
    ),
):
    """Search using both keyword and semantic retrieval."""

    try:
        service = HybridSearchService()

        results = service.search(
            query=query,
            top_k=top_k,
        )

        if not results:
            console.print("[yellow]No matching code found.[/yellow]")
            return

        table = Table(title=f"Hybrid Search: {query}")

        table.add_column("Symbol", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("File")
        table.add_column("Lines")
        table.add_column("Sources")
        table.add_column("RRF Score", justify="right")

        for result in results:
            table.add_row(
                result["name"],
                result["kind"],
                result["file_path"],
                (f"{result['start_line']}-{result['end_line']}"),
                ", ".join(result["sources"]),
                f"{result['score']:.5f}",
            )

        console.print(table)

        for index, result in enumerate(results, start=1):
            console.print(f"\n[cyan]Result {index}: {result['name']}[/cyan]")

            if result["text"]:
                console.print(result["text"])

    except ValueError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    except Exception as error:
        console.print(f"[red]Hybrid search failed: {error}[/red]")
        raise typer.Exit(code=1) from error


# --------------------------------------------------
# RETRIEVAL BENCHMARK
# --------------------------------------------------


@app.command("benchmark")
def benchmark_repository(
    query: str = typer.Argument(..., help="Search query"),
    repository_path: Path = typer.Option(
        Path("."),
        "--repository",
        "-r",
        help="Repository to benchmark",
    ),
    relevant: list[str] = typer.Option(
        ...,
        "--relevant",
        help="Relevant document ID. Repeat for multiple IDs.",
    ),
    top_k: int = typer.Option(3, "--top-k", min=1),
):
    """Benchmark keyword, semantic, and hybrid retrieval."""

    try:
        evaluator = RetrievalBenchmark()

        report = evaluator.evaluate_query(
            query=query,
            relevant_ids=set(relevant),
            repository_path=repository_path,
            k=top_k,
        )

        console.print("\n[bold cyan]Retrieval Benchmark[/bold cyan]")
        console.print(f"Query: {query}")
        console.print(f"Top K: {report['k']}")

        table = Table(title="Retrieval Strategy Comparison")

        table.add_column("Strategy")
        table.add_column("Precision", justify="right")
        table.add_column("Recall", justify="right")
        table.add_column("MRR", justify="right")

        for strategy, metrics in report["results"].items():
            table.add_row(
                strategy.capitalize(),
                f"{metrics['precision']:.3f}",
                f"{metrics['recall']:.3f}",
                f"{metrics['mrr']:.3f}",
            )

        console.print(table)

    except (ValueError, FileNotFoundError) as error:
        console.print(f"[red]Benchmark failed: {error}[/red]")
        raise typer.Exit(code=1) from error


# --------------------------------------------------
# BENCHMARK DATASET
# --------------------------------------------------


@app.command("benchmark-dataset")
def benchmark_dataset(
    dataset_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the benchmark JSON dataset",
    ),
):
    """Evaluate keyword, semantic, and hybrid retrieval."""

    try:
        evaluator = RetrievalBenchmark()
        report = evaluator.evaluate_dataset(dataset_path)

        console.print("\n[bold cyan]CodeMind Retrieval Benchmark[/bold cyan]")
        console.print(f"Queries evaluated: {report['total_queries']}")
        console.print(f"Top K: {report['k']}")

        table = Table(title="Aggregate Retrieval Performance")

        table.add_column("Strategy")
        table.add_column("Precision", justify="right")
        table.add_column("Recall", justify="right")
        table.add_column("MRR", justify="right")

        for strategy, metrics in report["aggregate"].items():
            table.add_row(
                strategy.capitalize(),
                f"{metrics['precision']:.3f}",
                f"{metrics['recall']:.3f}",
                f"{metrics['mrr']:.3f}",
            )

        console.print(table)

        console.print("\n[bold]Individual Query Results[/bold]")

        for item in report["individual_reports"]:
            console.print(f"\n[cyan]{item['query']}[/cyan]")

            for strategy, metrics in item["results"].items():
                console.print(
                    f"  {strategy}: "
                    f"P={metrics['precision']:.3f}, "
                    f"R={metrics['recall']:.3f}, "
                    f"MRR={metrics['mrr']:.3f}"
                )

    except (ValueError, FileNotFoundError) as error:
        console.print(f"[red]Benchmark failed: {error}[/red]")
        raise typer.Exit(code=1) from error


# --------------------------------------------------
# AGENT ASK
# --------------------------------------------------


@app.command()
def ask(
    query: str = typer.Argument(
        ...,
        help="Question about the repository",
    ),
    repository_path: Path = typer.Option(
        Path("."),
        "--repository",
        "-r",
        help="Repository path to investigate",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    top_k: int = typer.Option(
        5,
        "--top-k",
        min=1,
        help="Retrieval configuration",
    ),
):
    """Ask the CodeMind agent to investigate your codebase."""

    initialize_database()
    try:
        console.print("\n[bold cyan]CodeMind Agent is investigating...[/bold cyan]")

        agent = CodeMindAgent()

        result = agent.run(
            query=query,
            repository_path=str(repository_path.resolve()),
            top_k=top_k,
        )

        capture_ask(
            success=bool(result.get("answer")),
            iterations=result.get("iteration", 0),
            query_length=len(query),
            error=result.get("errors", [None])[0] if result.get("errors") else None,
        )

        console.print("\n[bold green]CodeMind Answer[/bold green]")
        console.print(result.get("answer") or "No answer generated.")

        observations = result.get("observations", [])

        if observations:
            console.print("\n[bold yellow]Investigation Evidence[/bold yellow]")

            for index, observation in enumerate(observations, start=1):
                console.print(
                    f"\n[cyan]Step {index}: "
                    f"{observation.get('tool', 'Unknown tool')}[/cyan]"
                )

                console.print(f"Input: {observation.get('input', '')}")

                results = observation.get("results", [])

                if results:
                    for item in results:
                        console.print(item)
                else:
                    console.print("[dim]No results returned.[/dim]")

                errors = observation.get("errors", [])

                if errors:
                    console.print(f"[red]Errors: {errors}[/red]")

        if result.get("errors"):
            console.print("\n[yellow]Investigation warnings:[/yellow]")

            for error in result["errors"]:
                console.print(f"- {error}")

    except Exception as error:
        console.print(f"\n[bold red]Agent failed: {error}[/bold red]")
        raise typer.Exit(code=1) from error


# --------------------------------------------------
# APPLICATION ENTRY POINT
# --------------------------------------------------


if __name__ == "__main__":
    app()
