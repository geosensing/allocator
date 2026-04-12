"""
Core algorithms for random walk itinerary generation on road networks.

Provides self-weighting random walks:
- At each intersection of degree d, choose next edge uniformly (probability 1/d)
- Traverse each edge fully
- Time-average converges to length-weighted spatial average (self-weighting)
- No inclusion probabilities needed
"""

from typing import Any

import networkx as nx
import numpy as np


def _get_node_pos(graph: nx.Graph, node: Any) -> tuple[float, float]:
    """
    Extract longitude/latitude from node attributes.

    Supports multiple attribute naming conventions:
    - x/y (OSMnx default)
    - lon/lat
    - longitude/latitude

    Args:
        graph: NetworkX graph
        node: Node identifier

    Returns:
        Tuple of (longitude, latitude)

    Raises:
        ValueError: If no valid coordinate attributes found
    """
    attrs = graph.nodes[node]

    if "x" in attrs and "y" in attrs:
        return float(attrs["x"]), float(attrs["y"])
    if "lon" in attrs and "lat" in attrs:
        return float(attrs["lon"]), float(attrs["lat"])
    if "longitude" in attrs and "latitude" in attrs:
        return float(attrs["longitude"]), float(attrs["latitude"])

    raise ValueError(
        f"Node {node} has no valid coordinate attributes. "
        "Expected x/y, lon/lat, or longitude/latitude."
    )


def _get_edge_length(graph: nx.Graph, u: Any, v: Any) -> float:
    """
    Get edge length in meters.

    Args:
        graph: NetworkX graph
        u: Source node
        v: Target node

    Returns:
        Edge length in meters

    Raises:
        ValueError: If edge has no length attribute
    """
    edge_data = graph.get_edge_data(u, v)
    if edge_data is None:
        raise ValueError(f"No edge between {u} and {v}")

    if isinstance(edge_data, dict) and "length" in edge_data:
        return float(edge_data["length"])

    # MultiGraph case: edge_data is dict of {key: attr_dict}
    if isinstance(edge_data, dict):
        for key in edge_data:
            if isinstance(edge_data[key], dict) and "length" in edge_data[key]:
                return float(edge_data[key]["length"])

    raise ValueError(f"Edge ({u}, {v}) has no 'length' attribute")


def _build_adjacency(graph: nx.Graph) -> dict[Any, list[tuple[Any, float]]]:
    """
    Build adjacency list with edge lengths for fast lookup.

    Args:
        graph: NetworkX graph with 'length' edge attribute

    Returns:
        Dict mapping node -> list of (neighbor, length) tuples
    """
    adj: dict[Any, list[tuple[Any, float]]] = {}
    for node in graph.nodes():
        neighbors = []
        for neighbor in graph.neighbors(node):
            try:
                length = _get_edge_length(graph, node, neighbor)
                neighbors.append((neighbor, length))
            except ValueError:
                continue
        adj[node] = neighbors
    return adj


def generate_walk(
    graph: nx.Graph,
    adj: dict[Any, list[tuple[Any, float]]],
    start_node: Any,
    walk_length_m: float,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """
    Generate a single random walk on the network.

    At each node with degree d, uniformly choose one of d neighbors.
    Dead ends (degree 1) cause reversal (correct behavior - dead-end segment
    receives double traversal).

    Args:
        graph: NetworkX graph
        adj: Pre-built adjacency dict from _build_adjacency
        start_node: Starting node ID
        walk_length_m: Target walk length in meters
        rng: Random number generator

    Returns:
        Dict with:
            - waypoints: List of (lon, lat, cumulative_distance_m)
            - edges_traversed: List of (from_node, to_node, length_m)
            - total_distance_m: Actual total distance walked
    """
    current = start_node
    lon, lat = _get_node_pos(graph, current)
    cum_dist = 0.0

    waypoints: list[tuple[float, float, float]] = [(lon, lat, 0.0)]
    edges_traversed: list[tuple[Any, Any, float]] = []

    while cum_dist < walk_length_m:
        neighbors = adj.get(current, [])
        if not neighbors:
            break

        idx = rng.integers(len(neighbors))
        next_node, edge_length = neighbors[idx]

        remaining = walk_length_m - cum_dist
        actual_traverse = min(edge_length, remaining)
        cum_dist += actual_traverse

        next_lon, next_lat = _get_node_pos(graph, next_node)

        if actual_traverse < edge_length:
            frac = actual_traverse / edge_length
            interp_lon = lon + frac * (next_lon - lon)
            interp_lat = lat + frac * (next_lat - lat)
            waypoints.append((interp_lon, interp_lat, cum_dist))
            edges_traversed.append((current, next_node, actual_traverse))
            break

        waypoints.append((next_lon, next_lat, cum_dist))
        edges_traversed.append((current, next_node, edge_length))

        current = next_node
        lon, lat = next_lon, next_lat

    return {
        "waypoints": waypoints,
        "edges_traversed": edges_traversed,
        "total_distance_m": cum_dist,
    }


def generate_walks(
    graph: nx.Graph,
    n_walks: int,
    walk_length_m: float,
    start_points: list[Any] | None = None,
    rng: np.random.Generator | None = None,
) -> list[dict[str, Any]]:
    """
    Generate multiple independent random walks on the network.

    Args:
        graph: NetworkX graph with node coordinates and edge lengths
        n_walks: Number of walks to generate
        walk_length_m: Target length for each walk in meters
        start_points: Optional list of starting node IDs. If provided,
            walks cycle through these points. If None, random nodes are chosen.
        rng: Random number generator for reproducibility

    Returns:
        List of walk dicts (see generate_walk for structure)
    """
    if rng is None:
        rng = np.random.default_rng()

    adj = _build_adjacency(graph)
    nodes = list(graph.nodes())

    if not nodes:
        return []

    walks = []
    for i in range(n_walks):
        if start_points:
            start_node = start_points[i % len(start_points)]
        else:
            start_node = nodes[rng.integers(len(nodes))]

        walk = generate_walk(graph, adj, start_node, walk_length_m, rng)
        walks.append(walk)

    return walks


def validate_graph(graph: nx.Graph) -> dict[str, Any]:
    """
    Validate that a graph has required attributes for random walks.

    Args:
        graph: NetworkX graph to validate

    Returns:
        Dict with validation info:
            - valid: bool
            - n_nodes: int
            - n_edges: int
            - nodes_with_coords: int
            - edges_with_length: int
            - total_network_length_m: float
            - errors: list of error messages
    """
    errors = []
    nodes_with_coords = 0
    edges_with_length = 0
    total_length = 0.0

    for node in graph.nodes():
        try:
            _get_node_pos(graph, node)
            nodes_with_coords += 1
        except ValueError:
            pass

    for u, v in graph.edges():
        try:
            length = _get_edge_length(graph, u, v)
            edges_with_length += 1
            total_length += length
        except ValueError:
            pass

    n_nodes = graph.number_of_nodes()
    n_edges = graph.number_of_edges()

    if nodes_with_coords == 0:
        errors.append(
            "No nodes have valid coordinate attributes (x/y, lon/lat, or longitude/latitude)"
        )
    elif nodes_with_coords < n_nodes:
        errors.append(f"Only {nodes_with_coords}/{n_nodes} nodes have coordinate attributes")

    if edges_with_length == 0:
        errors.append("No edges have 'length' attribute")
    elif edges_with_length < n_edges:
        errors.append(f"Only {edges_with_length}/{n_edges} edges have 'length' attribute")

    return {
        "valid": len(errors) == 0,
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "nodes_with_coords": nodes_with_coords,
        "edges_with_length": edges_with_length,
        "total_network_length_m": total_length,
        "errors": errors,
    }


def get_largest_connected_component(graph: nx.Graph) -> nx.Graph:
    """
    Return the largest connected component of the graph.

    Args:
        graph: NetworkX graph (may be disconnected)

    Returns:
        Subgraph containing only the largest connected component
    """
    if nx.is_connected(graph):
        return graph

    components = list(nx.connected_components(graph))
    largest = max(components, key=len)
    return graph.subgraph(largest).copy()
