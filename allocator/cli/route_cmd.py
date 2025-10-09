"""
Routing CLI commands.
"""

import click
from rich.console import Console

console = Console()


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--method",
    "-m",
    default="christofides",
    type=click.Choice(["christofides", "ortools", "osrm", "google"]),
    help="TSP solving method",
)
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
@click.option("--api-key", help="API key for Google services")
@click.option("--osrm-base-url", help="Custom OSRM server URL")
@click.pass_context
def tsp(ctx, input_file, method, distance, output, output_format, api_key, osrm_base_url):
    """Solve Traveling Salesman Problem (TSP) for geographic points."""
    from ..api import shortest_path
    from ..io.data_handler import DataHandler

    try:
        # Prepare kwargs
        kwargs = {}
        if api_key:
            kwargs["api_key"] = api_key
        if osrm_base_url:
            kwargs["osrm_base_url"] = osrm_base_url

        # Run TSP solver
        result = shortest_path(input_file, method=method, distance=distance, **kwargs)

        if ctx.obj.get("verbose"):
            console.print(f"[green]TSP solved using {method}[/green]")
            console.print(f"Total distance: {result.total_distance:.2f}")
            console.print(f"Route length: {len(result.route)} points")

        # Save results
        if output:
            DataHandler.save_results(result, output, format=output_format)
            console.print(f"[green]Results saved to {output}[/green]")
        else:
            console.print(f"\nOptimal route: {result.route}")
            console.print(f"Total distance: {result.total_distance:.2f}")

    except NotImplementedError:
        console.print(f"[yellow]{method} TSP solver will be implemented in Phase 5[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--distance",
    "-d",
    default="euclidean",
    type=click.Choice(["euclidean", "haversine"]),
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
def christofides(ctx, input_file, distance, output, output_format):
    """Solve TSP using Christofides algorithm (approximate)."""
    from ..api import tsp_christofides
    from ..io.data_handler import DataHandler

    try:
        result = tsp_christofides(input_file, distance=distance)

        if ctx.obj.get("verbose"):
            console.print("[green]TSP solved using Christofides algorithm[/green]")
            console.print(f"Total distance: {result.total_distance:.2f}")

        if output:
            DataHandler.save_results(result, output, format=output_format)
            console.print(f"[green]Results saved to {output}[/green]")
        else:
            console.print(f"\nOptimal route: {result.route}")
            console.print(f"Total distance: {result.total_distance:.2f}")

    except NotImplementedError:
        console.print("[yellow]Christofides TSP will be implemented in Phase 5[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--distance",
    "-d",
    default="euclidean",
    type=click.Choice(["euclidean", "haversine", "osrm"]),
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
@click.option("--osrm-base-url", help="Custom OSRM server URL")
@click.pass_context
def ortools(ctx, input_file, distance, output, output_format, osrm_base_url):
    """Solve TSP using Google OR-Tools (exact for small problems)."""
    from ..api import tsp_ortools
    from ..io.data_handler import DataHandler

    try:
        kwargs = {}
        if osrm_base_url:
            kwargs["osrm_base_url"] = osrm_base_url

        result = tsp_ortools(input_file, distance=distance, **kwargs)

        if ctx.obj.get("verbose"):
            console.print("[green]TSP solved using OR-Tools[/green]")
            console.print(f"Total distance: {result.total_distance:.2f}")

        if output:
            DataHandler.save_results(result, output, format=output_format)
            console.print(f"[green]Results saved to {output}[/green]")
        else:
            console.print(f"\nOptimal route: {result.route}")
            console.print(f"Total distance: {result.total_distance:.2f}")

    except NotImplementedError:
        console.print("[yellow]OR-Tools TSP will be implemented in Phase 5[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()
