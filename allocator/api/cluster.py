"""
Modern clustering API for allocator package.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ..core.algorithms import kmeans_cluster as _kmeans_cluster
from ..io.data_handler import DataHandler
from .types import ClusterResult


def cluster(
    data: str | pd.DataFrame | np.ndarray | list,
    n_clusters: int = 3,
    method: str = "kmeans",
    distance: str = "euclidean",
    random_state: int | None = None,
    **kwargs,
) -> ClusterResult:
    """
    Cluster geographic data points.

    Args:
        data: Input data (file path, DataFrame, numpy array, or list)
        n_clusters: Number of clusters to create
        method: Clustering method ('kmeans', 'kahip')
        distance: Distance metric ('euclidean', 'haversine', 'osrm', 'google')
        random_state: Random seed for reproducibility
        **kwargs: Additional arguments for specific methods

    Returns:
        ClusterResult with labels, centroids, and metadata

    Example:
        >>> result = cluster('data.csv', n_clusters=5, method='kmeans')
        >>> print(result.labels)  # Cluster assignments
        >>> print(result.centroids)  # Cluster centers
    """
    # Load and standardize data
    df = DataHandler.load_data(data)

    if method == "kmeans":
        return kmeans(
            df, n_clusters=n_clusters, distance=distance, random_state=random_state, **kwargs
        )
    elif method == "kahip":
        return kahip(
            df, n_clusters=n_clusters, distance=distance, random_state=random_state, **kwargs
        )
    else:
        raise ValueError(f"Unknown clustering method: {method}")


def kmeans(
    data: pd.DataFrame | np.ndarray | list,
    n_clusters: int = 3,
    distance: str = "euclidean",
    max_iter: int = 300,
    random_state: int | None = None,
    **kwargs,
) -> ClusterResult:
    """
    K-means clustering of geographic data.

    Args:
        data: Input data as DataFrame or numpy array
        n_clusters: Number of clusters
        distance: Distance metric ('euclidean', 'haversine', 'osrm', 'google')
        max_iter: Maximum iterations
        random_state: Random seed for reproducibility
        **kwargs: Additional distance-specific arguments

    Returns:
        ClusterResult with clustering information
    """
    # Ensure we have a DataFrame for output
    if isinstance(data, np.ndarray):
        df = DataHandler._from_numpy(data)
    elif isinstance(data, list):
        df = DataHandler._from_list(data)
    elif isinstance(data, (str, Path)):
        df = DataHandler.load_data(data)
    else:
        df = data.copy()

    # Run clustering algorithm
    result = _kmeans_cluster(
        df,
        n_clusters=n_clusters,
        distance_method=distance,
        max_iter=max_iter,
        random_state=random_state,
        **kwargs,
    )

    # Add cluster assignments to DataFrame
    df_result = df.copy()
    df_result["cluster"] = result["labels"]

    # Calculate inertia (sum of squared distances to centroids)
    inertia = None
    if distance == "euclidean":
        from ..distances.distance_matrix import euclidean_distance_matrix

        coords = df[["longitude", "latitude"]].values
        distances = euclidean_distance_matrix(coords, result["centroids"])
        inertia = np.sum(
            [distances[i, result["labels"][i]] ** 2 for i in range(len(result["labels"]))]
        )

    return ClusterResult(
        labels=result["labels"],
        centroids=result["centroids"],
        n_iter=result["iterations"],
        inertia=inertia,
        data=df_result,
        converged=result["converged"],
        metadata={
            "method": "kmeans",
            "distance": distance,
            "n_clusters": n_clusters,
            "max_iter": max_iter,
            "random_state": random_state,
        },
    )


def kahip(
    data: pd.DataFrame | np.ndarray,
    n_clusters: int = 3,
    distance: str = "euclidean",
    n_closest: int = 15,
    balance_edges: bool = False,
    buffoon: bool = False,
    random_state: int | None = None,
    **kwargs,
) -> ClusterResult:
    """
    KaHIP graph partitioning clustering.

    Args:
        data: Input data as DataFrame or numpy array
        n_clusters: Number of clusters
        distance: Distance metric
        n_closest: Number of closest neighbors to connect in graph
        balance_edges: Whether to balance edge weights
        buffoon: Whether to use buffoon mode
        random_state: Random seed for reproducibility
        **kwargs: Additional arguments

    Returns:
        ClusterResult with clustering information
    """
    from ..core.algorithms import kahip_cluster as _kahip_cluster

    # Ensure we have a DataFrame for output
    if isinstance(data, np.ndarray):
        df = DataHandler._from_numpy(data)
    elif isinstance(data, (str, Path)):
        df = DataHandler.load_data(data)
    else:
        df = data.copy()

    # Run clustering algorithm
    result = _kahip_cluster(
        df,
        n_clusters=n_clusters,
        distance_method=distance,
        n_closest=n_closest,
        seed=random_state,
        balance_edges=balance_edges,
        buffoon=buffoon,
        **kwargs,
    )

    # Add cluster assignments to DataFrame
    df_result = df.copy()
    df_result["cluster"] = result["labels"]

    return ClusterResult(
        labels=result["labels"],
        centroids=None,  # KaHIP doesn't compute centroids
        n_iter=1,  # KaHIP is not iterative
        inertia=None,
        data=df_result,
        converged=True,
        metadata={
            "method": "kahip",
            "distance": distance,
            "n_clusters": n_clusters,
            "n_closest": n_closest,
            "balance_edges": balance_edges,
            "buffoon": buffoon,
            "random_state": random_state,
        },
    )
