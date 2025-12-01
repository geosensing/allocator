"""
Clustering CLI commands.
"""

import click
from rich.console import Console

console = Console()


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--n-clusters", "-n", type=int, required=True, help="Number of clusters")
@click.option(
    "--distance",
    "-d",
    default="euclidean",
    type=click.Choice(["euclidean", "haversine", "osrm", "google"]),
    help="Distance metric to use",
)
@click.option("--max-iter", type=int, default=300, help="Maximum number of iterations")
@click.option("--random-state", type=int, help="Random seed for reproducibility")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--centroids", "-c", type=click.Path(), help="Centroids output file path")
@click.option("--plot", is_flag=True, help="Show clustering plot")
@click.option("--save-plot", type=click.Path(), help="Save plot to file")
@click.option(
    "--format",
    "output_format",
    default="csv",
    type=click.Choice(["csv", "json"]),
    help="Output format",
)
@click.pass_context
def kmeans(
    ctx,
    input_file,
    n_clusters,
    distance,
    max_iter,
    random_state,
    output,
    centroids,
    plot,
    save_plot,
    output_format,
):
    """K-means clustering of geographic data."""
    from ..api import kmeans as kmeans_func
    from ..io.data_handler import DataHandler
    from ..viz.plotting import plot_clusters

    try:
        # Run clustering
        result = kmeans_func(
            input_file,
            n_clusters=n_clusters,
            distance=distance,
            max_iter=max_iter,
            random_state=random_state,
        )

        if ctx.obj.get("verbose"):
            console.print(f"[green]K-means converged: {result.converged}[/green]")
            console.print(f"Iterations: {result.n_iter}")
            if result.inertia:
                console.print(f"Inertia: {result.inertia:.2f}")

        # Save results
        if output:
            DataHandler.save_results(result, output, format=output_format)
            console.print(f"[green]Results saved to {output}[/green]")

        # Save centroids
        if centroids:
            import pandas as pd

            centroids_df = pd.DataFrame(result.centroids, columns=["longitude", "latitude"])
            if output_format == "csv":
                centroids_df.to_csv(centroids, index=False)
            else:
                centroids_df.to_json(centroids, orient="records", indent=2)
            console.print(f"[green]Centroids saved to {centroids}[/green]")

        # Plotting
        if plot or save_plot:
            plot_clusters(
                result.data,
                result.labels,
                result.centroids,
                title=f"K-means Clustering (n={n_clusters})",
                save_path=save_plot,
                show=plot,
            )
            if save_plot:
                console.print(f"[green]Plot saved to {save_plot}[/green]")

        if not output:
            console.print("\nFirst 10 results:")
            console.print(result.data.head(10).to_string())

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort() from e
