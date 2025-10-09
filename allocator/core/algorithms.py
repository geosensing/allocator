"""
Pure algorithm implementations without CLI, plotting, or file I/O.
"""

from __future__ import annotations

import os
import shlex
import subprocess
from random import randint

import networkx as nx
import numpy as np
import pandas as pd

from ..distances.distance_matrix import get_distance_matrix


def initialize_centroids(points: np.ndarray, k: int, random_state: int | None = None) -> np.ndarray:
    """
    Initialize k centroids by randomly selecting from points.

    Args:
        points: Input points array with shape [n, 2]
        k: Number of centroids
        random_state: Random seed for reproducibility

    Returns:
        Array of k initial centroids
    """
    if random_state is not None:
        rng = np.random.RandomState(random_state)
        rng_state = rng.get_state()
        np.random.set_state(rng_state)

    centroids = points.copy()
    np.random.shuffle(centroids)
    return centroids[:k]


def move_centroids(points: np.ndarray, closest: np.ndarray, centroids: np.ndarray) -> np.ndarray:
    """
    Update centroids to the mean of their assigned points.

    Args:
        points: All data points
        closest: Array indicating which centroid each point belongs to
        centroids: Current centroids

    Returns:
        Updated centroids
    """
    new_centroids = [points[closest == k].mean(axis=0) for k in range(centroids.shape[0])]

    # Handle empty clusters by keeping old centroid
    for i, c in enumerate(new_centroids):
        if np.isnan(c).any():
            new_centroids[i] = centroids[i]

    return np.array(new_centroids)


def kmeans_cluster(
    data: pd.DataFrame | np.ndarray,
    n_clusters: int,
    distance_method: str = "euclidean",
    max_iter: int = 300,
    random_state: int | None = None,
    **distance_kwargs,
) -> dict:
    """
    Pure K-means clustering implementation.

    Args:
        data: Input data as DataFrame with longitude/latitude or numpy array [n, 2]
        n_clusters: Number of clusters
        distance_method: Distance calculation method
        max_iter: Maximum iterations
        random_state: Random seed
        **distance_kwargs: Additional arguments for distance calculation

    Returns:
        Dictionary with 'labels', 'centroids', 'iterations', 'converged'
    """
    # Convert DataFrame to numpy array if needed
    if isinstance(data, pd.DataFrame):
        if "longitude" in data.columns and "latitude" in data.columns:
            X = data[["longitude", "latitude"]].values
        else:
            raise ValueError("DataFrame must contain 'longitude' and 'latitude' columns")
    else:
        X = np.asarray(data)

    # Initialize centroids
    centroids = initialize_centroids(X, n_clusters, random_state)
    old_centroids = centroids.copy()

    for i in range(max_iter):
        # Calculate distances and assign points to closest centroids
        distances = get_distance_matrix(X, centroids, method=distance_method, **distance_kwargs)
        labels = np.argmin(distances, axis=1)

        # Update centroids
        centroids = move_centroids(X, labels, centroids)

        # Check for convergence
        if np.allclose(old_centroids, centroids, rtol=1e-4):
            return {
                "labels": labels,
                "centroids": centroids,
                "iterations": i + 1,
                "converged": True,
            }

        old_centroids = centroids.copy()

    return {"labels": labels, "centroids": centroids, "iterations": max_iter, "converged": False}


def kahip_cluster(
    data: pd.DataFrame | np.ndarray,
    n_clusters: int,
    distance_method: str = "euclidean",
    n_closest: int = 15,
    seed: int | None = None,
    balance_edges: bool = False,
    buffoon: bool = False,
    kahip_dir: str = "./KaHIP/src",
    **distance_kwargs,
) -> dict:
    """
    Pure KaHIP clustering implementation.

    Args:
        data: Input data as DataFrame with longitude/latitude or numpy array [n, 2]
        n_clusters: Number of clusters
        distance_method: Distance calculation method
        n_closest: Number of closest neighbors to connect in graph
        seed: Random seed for KaHIP
        balance_edges: Whether to use balanced edge partitioning
        buffoon: Whether to use buffoon mode
        kahip_dir: Path to KaHIP directory
        **distance_kwargs: Additional arguments for distance calculation

    Returns:
        Dictionary with 'labels' and 'graph' keys
    """
    # Convert DataFrame to numpy array if needed
    if isinstance(data, pd.DataFrame):
        if "longitude" in data.columns and "latitude" in data.columns:
            X = data[["longitude", "latitude"]].values
        else:
            raise ValueError("DataFrame must contain 'longitude' and 'latitude' columns")
    else:
        X = np.asarray(data)

    if seed is None:
        seed = randint(0, 0xFFFF)

    # Get distance matrix
    distances = get_distance_matrix(X, X, method=distance_method, **distance_kwargs)

    if distances is None:
        raise ValueError("Could not calculate distance matrix")

    # FIXME: KaHIP doesn't like complete graph. Only N closest distances will be used.
    for d in distances:
        s = np.argsort(d)
        for i in s[n_closest:]:
            d[i] = 0

    # Create graph
    G = nx.from_numpy_array(distances)

    if buffoon:
        # Use KaHIP buffoon version
        labels = _run_kahip_buffoon(G, n_clusters, seed, kahip_dir)
    else:
        # Use Python wrapper version
        labels = _run_kahip_wrapper(G, n_clusters, seed, balance_edges)

    return {"labels": labels, "graph": G}


def _run_kahip_buffoon(G: nx.Graph, n_clusters: int, seed: int, kahip_dir: str) -> np.ndarray:
    """Run KaHIP buffoon version."""
    # Export Graph to METIS text file format
    with open("metis.graph", "w") as f:
        f.write(f"{len(G.nodes())} {len(G.edges())} 11\n")
        for n in G.nodes():
            a = ["1"]
            for e in G.edges(n, data=True):
                a.append(str(e[1] + 1))
                a.append(str(int(e[2]["weight"])))
            f.write(" ".join(a) + "\n")

    os.putenv("LD_LIBRARY_PATH", os.path.join(kahip_dir, "extern/argtable-2.10/lib"))

    buffoon_cmd = (
        f"mpirun -n {n_clusters} {kahip_dir}/optimized/buffoon metis.graph "
        f"--seed {seed} --k {n_clusters} --preconfiguration=strong "
        f"--max_num_threads={n_clusters}"
    )

    print(f"Command line: '{buffoon_cmd}'")

    # Execute command
    p = subprocess.Popen(
        shlex.split(buffoon_cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True
    )
    out, err = p.communicate()

    print(f"Output: {out.decode()}")

    # Read results
    ldf = pd.read_csv(f"tmppartition{n_clusters}", header=None)
    labels = ldf[0].values

    # Clean up temporary files
    try:
        os.remove("metis.graph")
        os.remove(f"tmppartition{n_clusters}")
    except FileNotFoundError:
        pass

    return labels


def _run_kahip_wrapper(G: nx.Graph, n_clusters: int, seed: int, balance_edges: bool) -> np.ndarray:
    """Run KaHIP using Python wrapper."""
    try:
        from kahipwrapper import kaHIP
    except ImportError:
        raise ImportError(
            "kahipwrapper package is required for KaHIP clustering. "
            "Install with: pip install kahipwrapper"
        )

    ncount = len(G)
    vwgt = None
    xadj = []
    adjcwgt = []
    adjncy = []
    nparts = n_clusters
    imbalance = 0.03
    suppress_output = False
    mode = kaHIP.STRONG

    for n in G.nodes():
        xadj.append(len(adjncy))
        for e in G.edges(n, data=True):
            to = e[1]
            adjncy.append(to)
            w = int(e[2]["weight"])
            adjcwgt.append(w)
    xadj.append(len(adjncy))

    if balance_edges:
        edgecut, part = kaHIP.kaffpa_balance_NE(
            ncount, vwgt, xadj, adjcwgt, adjncy, nparts, imbalance, suppress_output, seed, mode
        )
    else:
        edgecut, part = kaHIP.kaffpa(
            ncount, vwgt, xadj, adjcwgt, adjncy, nparts, imbalance, suppress_output, seed, mode
        )

    return np.array(part)


def sort_by_distance_assignment(
    data: pd.DataFrame | np.ndarray,
    centroids: np.ndarray,
    distance_method: str = "euclidean",
    **distance_kwargs,
) -> np.ndarray:
    """
    Assign points to closest centroids (used by sort_by_distance).

    Args:
        data: Input data as DataFrame or numpy array
        centroids: Centroid locations
        distance_method: Distance calculation method
        **distance_kwargs: Additional arguments for distance calculation

    Returns:
        Array of cluster assignments
    """
    # Convert DataFrame to numpy array if needed
    if isinstance(data, pd.DataFrame):
        if "longitude" in data.columns and "latitude" in data.columns:
            X = data[["longitude", "latitude"]].values
        else:
            raise ValueError("DataFrame must contain 'longitude' and 'latitude' columns")
    else:
        X = np.asarray(data)

    # Calculate distances and assign to closest
    distances = get_distance_matrix(X, centroids, method=distance_method, **distance_kwargs)
    labels = np.argmin(distances, axis=1)

    return labels


def calculate_cluster_statistics(
    data: pd.DataFrame, labels: np.ndarray, distance_method: str = "euclidean", **distance_kwargs
) -> list[dict]:
    """
    Calculate statistics for each cluster (used by comparison functions).

    Args:
        data: Input data with coordinates
        labels: Cluster assignments
        distance_method: Distance calculation method
        **distance_kwargs: Additional arguments for distance calculation

    Returns:
        List of dictionaries with cluster statistics
    """
    import networkx as nx

    results = []
    X = data[["longitude", "latitude"]].values

    for cluster_id in sorted(np.unique(labels)):
        cluster_points = X[labels == cluster_id]
        n_points = len(cluster_points)

        if n_points <= 1:
            # Skip clusters with 0 or 1 points
            continue

        # Calculate distance matrix for this cluster
        distances = get_distance_matrix(
            cluster_points, cluster_points, method=distance_method, **distance_kwargs
        )

        if distances is None:
            continue

        # Create graph and calculate MST
        G = nx.from_numpy_matrix(distances)
        T = nx.minimum_spanning_tree(G)

        graph_weight = int(G.size(weight="weight") / 1000)
        mst_weight = int(T.size(weight="weight") / 1000)

        results.append(
            {
                "label": cluster_id,
                "n": n_points,
                "graph_weight": graph_weight,
                "mst_weight": mst_weight,
            }
        )

    return results
