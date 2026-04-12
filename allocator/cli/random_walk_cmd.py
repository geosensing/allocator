"""
Random walk CLI command for itinerary generation on road networks.
"""

import click
import networkx as nx
from rich.console import Console
from rich.table import Table

console = Console()


@click.command()
@click.argument("graph_file", type=click.Path(exists=True))
@click.option(
    "--n-walks",
    "-n",
    type=int,
    default=15,
    help="Number of independent walks to generate (default 15)",
)
@click.option(
    "--length",
    "-l",
    type=float,
    default=5000.0,
    help="Target walk length in meters (default 5000)",
)
@click.option(
    "--seed",
    type=int,
    help="Random seed for reproducibility",
)
@click.option(
    "--no-largest-component",
    is_flag=True,
    help="Don't restrict to largest connected component",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output CSV file for waypoints",
)
@click.option(
    "--format",
    "output_format",
    default="csv",
    type=click.Choice(["csv", "json"]),
    help="Output format (default csv)",
)
@click.pass_context
def random_walk_cmd(
    ctx: click.Context,
    graph_file: str,
    n_walks: int,
    length: float,
    seed: int | None,
    no_largest_component: bool,
    output: str | None,
    output_format: str,
) -> None:
    """Generate random walk itineraries from a road network graph.

    GRAPH_FILE should be a GraphML, GML, or pickle file containing a NetworkX graph
    with node coordinates (x/y, lon/lat, or longitude/latitude) and edge lengths.

    Example:
        allocator random-walk network.graphml -n 15 --length 5000 -o walks.csv
    """
    from ..api.random_walk import random_walk
    from ..io.data_handler import DataHandler

    try:
        if graph_file.endswith(".graphml"):
            graph = nx.read_graphml(graph_file)
        elif graph_file.endswith(".gml"):
            graph = nx.read_gml(graph_file)
        elif graph_file.endswith(".gpickle") or graph_file.endswith(".pkl"):
            import pickle

            with open(graph_file, "rb") as f:
                graph = pickle.load(f)
        else:
            console.print(
                "[red]Error: Unsupported graph format. Use .graphml, .gml, or .gpickle/.pkl[/red]"
            )
            raise click.Abort()

        result = random_walk(
            graph,
            n_walks=n_walks,
            walk_length_m=length,
            seed=seed,
            use_largest_component=not no_largest_component,
        )

        table = Table(title="Random Walk Summary")
        table.add_column("Walk", style="cyan")
        table.add_column("Waypoints", style="green")
        table.add_column("Distance (m)", style="magenta")

        for i, walk in enumerate(result.walks):
            table.add_row(
                str(i),
                str(len(walk["waypoints"])),
                f"{walk['total_distance_m']:.1f}",
            )

        console.print(table)
        console.print(f"\nTotal: {len(result.walks)} walks")
        console.print(
            f"Network: {result.metadata['n_nodes']} nodes, {result.metadata['n_edges']} edges"
        )
        console.print(f"Avg distance: {result.metadata['avg_actual_distance_m']:.1f}m")

        if ctx.obj.get("verbose"):
            console.print(f"Target length: {length}m")
            console.print(f"Total network length: {result.metadata['total_network_length_m']:.1f}m")
            console.print(f"Seed: {seed}")

        if output:
            DataHandler.save_results(result, output, format=output_format)
            console.print(f"[green]Results saved to {output}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort() from e
