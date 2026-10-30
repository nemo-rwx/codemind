from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from codemind.indexer.semantic import SemanticIndexer

from codemind.indexer.service import RepositoryIndexer
from codemind.scanner.service import RepositoryScanner
from codemind.search.service import CodeSearchService
from codemind.search.semantic import SemanticSearchService
from codemind.search.hybrid import HybridSearchService


app = typer.Typer(
    name="codemind",
    help="Agentic AI powered Codebase Intelligence CLI",
    no_args_is_help=True,
)

console = Console()


@app.command()
def version():
    """Display CodeMind version."""
    console.print("[bold green]CodeMind v0.1.0[/bold green]")


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

        if result["errors"]:
            console.print("\n[yellow]Warnings / Errors:[/yellow]")
            for error in result["errors"]:
                console.print(f"- {error}")

    except Exception as error:
        console.print(f"[bold red]Indexing failed: {error}[/bold red]")
        raise typer.Exit(code=1) from error


@app.command()
def search(
    query: str = typer.Argument(
        ...,
        help="Class, method, or function name to search",
    ),
):
    """Search indexed code symbols."""

    search_service = CodeSearchService()
    results = search_service.search(query)

    if not results:
        console.print(f"[yellow]No symbols found for: {query}[/yellow]")
        return

    table = Table(title=f"Search Results: {query}")

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


@app.command()
def search(
    query: str = typer.Argument(
        ...,
        help="Class, method, or function name to search",
    ),
):
    """Search indexed code symbols."""

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


if __name__ == "__main__":
    app()
