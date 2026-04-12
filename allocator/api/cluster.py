"""
Modern clustering API for allocator package.
"""

from pathlib import Path

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
        method: Clustering method ('kmeans')
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
    else:
        raise ValueError(f"Unknown clustering method: {method}. Available methods: 'kmeans'")


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
        distance: Distance metric (stored in metadata only; clustering uses Euclidean)
        max_iter: Maximum iterations
        random_state: Random seed for reproducibility
        **kwargs: Additional arguments (unused, kept for API compatibility)

    Returns:
        ClusterResult with clustering information
    """
    del kwargs

    if isinstance(data, np.ndarray):
        df = DataHandler._from_numpy(data)
    elif isinstance(data, list):
        df = DataHandler._from_list(data)
    elif isinstance(data, (str, Path)):
        df = DataHandler.load_data(data)
    else:
        df = data.copy()

    result = _kmeans_cluster(
        df,
        n_clusters=n_clusters,
        max_iter=max_iter,
        random_state=random_state,
    )

    df_result = df.copy()
    df_result["cluster"] = result["labels"]

    return ClusterResult(
        labels=result["labels"],
        centroids=result["centroids"],
        n_iter=result["iterations"],
        inertia=result["inertia"],
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
