"""
Modern CLI interface for allocator package using Click.
"""

import click
from rich.console import Console
from rich.table import Table

from .. import __version__

console = Console()


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose):
    """
    Allocator v1.0 - Modern geographic task allocation, clustering, and routing.

    Examples:
        allocator cluster kmeans data.csv -n 5
        allocator route tsp points.csv --method ortools
        allocator sort points.csv --workers workers.csv
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.group()
def cluster():
    """Cluster geographic data points."""
    pass


@cli.group()
def route():
    """Find shortest paths through points (TSP)."""
    pass


# Import and register subcommands
from .cluster_cmd import kmeans, kahip
from .route_cmd import tsp, christofides, ortools

cluster.add_command(kmeans)
cluster.add_command(kahip)
route.add_command(tsp)
route.add_command(christofides)
route.add_command(ortools)


@cli.command()
@click.argument("points", type=click.Path(exists=True))
@click.option("--workers", "-w", type=click.Path(exists=True), help="Worker locations file")
@click.option("--by-worker", is_flag=True, help="Sort points by worker instead of workers by point")
@click.option(
    "--distance",
    "-d",
    default="euclidean",
    type=click.Choice(["euclidean", "haversine", "osrm", "google"]),
    help="Distance metric to use",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--format",
    "output_format",
    default="csv",
    type=click.Choice(["csv", "json"]),
    help="Output format",
)
@click.pass_context
def sort(ctx, points, workers, by_worker, distance, output, output_format):
    """Sort points by distance to workers or assign to closest."""
    from ..api import sort_by_distance, assign_to_closest
    from ..io.data_handler import DataHandler

    try:
        if workers:
            if by_worker:
                result = sort_by_distance(points, workers, by_worker=True, distance=distance)
            else:
                result = sort_by_distance(points, workers, by_worker=False, distance=distance)
        else:
            console.print("[red]Error: --workers option is required[/red]")
            raise click.Abort()

        # Save results
        if output:
            DataHandler.save_results(result, output, format=output_format)
            console.print(f"[green]Results saved to {output}[/green]")
        else:
            console.print(result.data.head())

        if ctx.obj["verbose"]:
            console.print(f"Processed {len(result.data)} assignments")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--algorithms",
    "-a",
    default="kmeans,kahip",
    help="Comma-separated list of algorithms to compare",
)
@click.option("--n-clusters", "-n", type=int, required=True, help="Number of clusters")
@click.option(
    "--distance",
    "-d",
    default="euclidean",
    type=click.Choice(["euclidean", "haversine", "osrm"]),
    help="Distance metric to use",
)
@click.option("--output", "-o", type=click.Path(), help="Output file for comparison results")
@click.pass_context
def compare(ctx, input_file, algorithms, n_clusters, distance, output):
    """Compare clustering algorithms."""
    from ..api import cluster

    try:
        algos = [algo.strip() for algo in algorithms.split(",")]
        results = {}

        for algo in algos:
            if algo in ["kmeans", "kahip"]:
                console.print(f"Running {algo} clustering...")
                result = cluster(input_file, n_clusters=n_clusters, method=algo, distance=distance)
                results[algo] = result
            else:
                console.print(f"[yellow]Warning: Unknown algorithm '{algo}', skipping[/yellow]")

        # Create comparison table
        table = Table(title="Clustering Comparison")
        table.add_column("Algorithm", style="cyan")
        table.add_column("Converged", style="green")
        table.add_column("Iterations", style="magenta")
        table.add_column("Inertia", style="yellow")

        for algo, result in results.items():
            converged = "Yes" if result.converged else "No"
            iterations = str(result.n_iter)
            inertia = f"{result.inertia:.2f}" if result.inertia else "N/A"
            table.add_row(algo, converged, iterations, inertia)

        console.print(table)

        if output:
            # Save detailed comparison
            comparison_data = []
            for algo, result in results.items():
                df = result.data.copy()
                df["algorithm"] = algo
                comparison_data.append(df)

            import pandas as pd

            combined_df = pd.concat(comparison_data, ignore_index=True)
            combined_df.to_csv(output, index=False)
            console.print(f"[green]Detailed results saved to {output}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


if __name__ == "__main__":
    cli()
