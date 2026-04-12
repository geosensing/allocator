"""
Itinerary CLI command for route generation.
"""

import click
from rich.console import Console
from rich.table import Table

from ..api.types import VALID_METHODS

console = Console()


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--method",
    type=click.Choice(VALID_METHODS),
    default="greedy_nn",
    help="Itinerary generation method",
)
@click.option(
    "--max-distance",
    "-m",
    type=float,
    help="Maximum distance per itinerary (required for greedy_nn, softmax_greedy)",
)
@click.option(
    "--n-itineraries",
    "-n",
    type=int,
    help="Number of itineraries (required for partition methods)",
)
@click.option(
    "--distance",
    "-d",
    default="haversine",
    type=click.Choice(["euclidean", "haversine", "osrm", "google"]),
    help="Distance metric to use",
)
@click.option(
    "--start-method",
    "-s",
    default="random",
    type=click.Choice(["random", "first", "furthest"]),
    help="Method for picking starting points (budget methods only)",
)
@click.option(
    "--temperature",
    "-t",
    type=float,
    default=0.1,
    help="Softmax temperature (softmax_greedy only)",
)
@click.option(
    "--n-strata",
    type=int,
    default=4,
    help="Number of strata (stratified only)",
)
@click.option(
    "--no-optimize",
    is_flag=True,
    help="Skip TSP route optimization (partition methods)",
)
@click.option("--seed", type=int, help="Random seed for reproducibility")
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
def itinerary(
    ctx: click.Context,
    input_file: str,
    method: str,
    max_distance: float | None,
    n_itineraries: int | None,
    distance: str,
    start_method: str,
    temperature: float,
    n_strata: int,
    no_optimize: bool,
    seed: int | None,
    output: str | None,
    output_format: str,
    api_key: str | None,
    osrm_base_url: str | None,
) -> None:
    """Generate itineraries from geographic points."""
    from ..api.itinerary import create_itineraries
    from ..io.data_handler import DataHandler

    try:
        kwargs = {}
        if api_key:
            kwargs["api_key"] = api_key
        if osrm_base_url:
            kwargs["osrm_base_url"] = osrm_base_url

        result = create_itineraries(
            input_file,
            method=method,
            max_distance=max_distance,
            n_itineraries=n_itineraries,
            distance=distance,
            start_method=start_method,
            temperature=temperature,
            n_strata=n_strata,
            optimize_routes=not no_optimize,
            seed=seed,
            **kwargs,
        )

        table = Table(title="Itinerary Summary")
        table.add_column("Itinerary", style="cyan")
        table.add_column("Points", style="green")
        table.add_column("Distance (m)", style="magenta")

        for i, (route, dist) in enumerate(zip(result.itineraries, result.distances, strict=True)):
            table.add_row(str(i), str(len(route)), f"{dist:.1f}")

        console.print(table)
        console.print(
            f"\nTotal: {len(result.itineraries)} itineraries, {result.metadata['n_points']} points"
        )

        if ctx.obj.get("verbose"):
            console.print(f"Distance metric: {distance}")
            console.print(f"Max distance: {max_distance:.0f}m")
            console.print(f"Avg distance: {result.metadata['avg_distance']:.1f}m")
            console.print(
                f"Avg points per itinerary: {result.metadata['avg_points_per_itinerary']:.1f}"
            )

        if output:
            DataHandler.save_results(result, output, format=output_format)
            console.print(f"[green]Results saved to {output}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort() from e
