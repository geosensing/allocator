"""
API for random walk itinerary generation on road networks.
"""

from typing import Any

import networkx as nx
import numpy as np
import pandas as pd

from ..core.random_walk import (
    generate_walks,
    get_largest_connected_component,
    validate_graph,
)
from .types import RandomWalkResult


def random_walk(
    graph: nx.Graph,
    n_walks: int = 15,
    walk_length_m: float = 5000.0,
    start_points: list[Any] | None = None,
    seed: int | None = None,
    use_largest_component: bool = True,
) -> RandomWalkResult:
    """
    Generate self-weighting random walk itineraries on a road network graph.

    Random walks on road networks have a self-weighting property: at each
    intersection of degree d, choosing the next edge uniformly (probability 1/d)
    ensures that the time-average along the walk converges to a length-weighted
    spatial average. This eliminates the need for explicit inclusion probabilities.

    Args:
        graph: NetworkX graph from OSMnx or geo-sampling. Must have:
            - Node attributes: x/y, lon/lat, or longitude/latitude
            - Edge attributes: length (in meters)
        n_walks: Number of independent walks to generate (default 15)
        walk_length_m: Target length of each walk in meters (default 5000.0)
        start_points: Optional list of starting node IDs. If provided, walks
            cycle through these points (useful for GRTS-selected starting locations).
            If None, random nodes are chosen uniformly.
        seed: Random seed for reproducibility
        use_largest_component: If True (default), use only the largest connected
            component of the graph to avoid getting stuck in disconnected regions.

    Returns:
        RandomWalkResult containing:
            - walks: List of walk dicts, each with:
                - waypoints: List of (lon, lat, cumulative_distance_m) tuples
                - edges_traversed: List of (from_node, to_node, length_m) tuples
                - total_distance_m: Actual distance walked
            - data: DataFrame with all waypoints:
                - walk_id: Walk index
                - sequence: Waypoint sequence number within walk
                - longitude: Waypoint longitude
                - latitude: Waypoint latitude
                - cumulative_distance_m: Distance from walk start
            - metadata: Dict with:
                - n_walks: Number of walks generated
                - walk_length_m: Target walk length
                - total_network_length_m: Sum of all edge lengths
                - n_nodes: Number of nodes in graph
                - n_edges: Number of edges in graph
                - seed: Random seed used
                - avg_actual_distance_m: Mean actual walk distance
                - start_points_provided: Whether start_points was provided

    Raises:
        ValueError: If graph has no valid nodes or edges

    Example:
        >>> import networkx as nx
        >>> import allocator
        >>>
        >>> # Create a simple test graph
        >>> G = nx.Graph()
        >>> G.add_node(0, longitude=100.0, latitude=13.0)
        >>> G.add_node(1, longitude=100.1, latitude=13.0)
        >>> G.add_edge(0, 1, length=1000.0)
        >>>
        >>> result = allocator.random_walk(G, n_walks=5, walk_length_m=500.0, seed=42)
        >>> len(result.walks)
        5
    """
    validation = validate_graph(graph)
    if not validation["valid"]:
        raise ValueError(f"Invalid graph: {'; '.join(validation['errors'])}")

    working_graph = graph
    if use_largest_component:
        working_graph = get_largest_connected_component(graph)
        if working_graph.number_of_nodes() < graph.number_of_nodes():
            validation = validate_graph(working_graph)

    rng = np.random.default_rng(seed)

    walks = generate_walks(
        working_graph,
        n_walks=n_walks,
        walk_length_m=walk_length_m,
        start_points=start_points,
        rng=rng,
    )

    rows = []
    for walk_id, walk in enumerate(walks):
        for seq, (lon, lat, cum_dist) in enumerate(walk["waypoints"]):
            rows.append(
                {
                    "walk_id": walk_id,
                    "sequence": seq,
                    "longitude": lon,
                    "latitude": lat,
                    "cumulative_distance_m": cum_dist,
                }
            )

    data = pd.DataFrame(rows)

    actual_distances = [w["total_distance_m"] for w in walks]

    metadata = {
        "n_walks": len(walks),
        "walk_length_m": walk_length_m,
        "total_network_length_m": validation["total_network_length_m"],
        "n_nodes": validation["n_nodes"],
        "n_edges": validation["n_edges"],
        "seed": seed,
        "avg_actual_distance_m": float(np.mean(actual_distances)) if walks else 0.0,
        "start_points_provided": start_points is not None,
    }

    return RandomWalkResult(
        walks=walks,
        data=data,
        metadata=metadata,
    )
