"""
Pure algorithm implementations without CLI, plotting, or file I/O.
"""

from typing import Any

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from ..distances import get_distance_matrix


def kmeans_cluster(
    data: pd.DataFrame | np.ndarray,
    n_clusters: int,
    max_iter: int = 300,
    random_state: int | None = None,
) -> dict[str, Any]:
    """
    K-means clustering using sklearn.

    Args:
        data: Input data as DataFrame or numpy array
        n_clusters: Number of clusters
        max_iter: Maximum iterations
        random_state: Random seed for reproducibility

    Returns:
        Dictionary with 'labels', 'centroids', 'iterations', 'converged', 'inertia'
    """
    if isinstance(data, pd.DataFrame):
        if "longitude" in data.columns and "latitude" in data.columns:
            X = data[["longitude", "latitude"]].values
        else:
            raise ValueError("DataFrame must contain 'longitude' and 'latitude' columns")
    else:
        X = np.asarray(data)

    kmeans = KMeans(n_clusters=n_clusters, max_iter=max_iter, random_state=random_state, n_init="auto")
    kmeans.fit(X)

    return {
        "labels": kmeans.labels_,
        "centroids": kmeans.cluster_centers_,
        "iterations": kmeans.n_iter_,
        "converged": kmeans.n_iter_ < max_iter,
        "inertia": kmeans.inertia_,
    }


def sort_by_distance_assignment(
    data: pd.DataFrame | np.ndarray,
    centroids: np.ndarray,
    distance_method: str = "euclidean",
    **distance_kwargs: Any,
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
    labels: np.ndarray = np.argmin(distances, axis=1)

    return labels


def calculate_cluster_statistics(
    data: pd.DataFrame,
    labels: np.ndarray,
    distance_method: str = "euclidean",
    **distance_kwargs: Any,
) -> list[dict[str, Any]]:
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

        # Create graph and calculate MST
        G = nx.from_numpy_array(distances)
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
