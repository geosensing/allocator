"""
Pure algorithm implementations without CLI, plotting, or file I/O.
"""

from __future__ import annotations

from typing import Any

import networkx as nx
import numpy as np
import pandas as pd

from ..distances import get_distance_matrix

try:
    from sklearn.cluster import KMeans
    from sklearn.utils.validation import check_array

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    KMeans = object

    def check_array(X: Any, **kwargs: Any) -> np.ndarray:
        return np.asarray(X)


def initialize_centroids(
    points: np.ndarray,
    k: int,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """
    Initialize k centroids by randomly selecting from points.

    Args:
        points: Input points array with shape [n, 2]
        k: Number of centroids
        rng: Random number generator for reproducibility

    Returns:
        Array of k initial centroids
    """
    if rng is None:
        rng = np.random.default_rng()
    indices = rng.choice(len(points), size=k, replace=False)
    return points[indices].copy()


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


class CustomKMeans(KMeans):
    """
    Custom K-means implementation that supports geographic distance metrics.

    This class extends sklearn's KMeans to work with custom distance functions
    including haversine, OSRM, and Google Maps API distances.
    """

    cluster_centers_: np.ndarray
    labels_: np.ndarray
    n_iter_: int

    def __init__(
        self,
        n_clusters: int = 8,
        distance_method: str = "euclidean",
        max_iter: int = 300,
        random_state: int | None = None,
        **distance_kwargs: Any,
    ) -> None:
        if HAS_SKLEARN:
            super().__init__(n_clusters=n_clusters, max_iter=max_iter, random_state=random_state)
        self.distance_method = distance_method
        self.distance_kwargs = distance_kwargs
        self.n_clusters = n_clusters

    def _transform(self, X: np.ndarray) -> np.ndarray:
        """Override sklearn's distance calculation to use custom metrics."""
        if not HAS_SKLEARN:
            raise ImportError(
                "sklearn is required for CustomKMeans. Install with: pip install 'allocator[algorithms]'"
            )

        distances = get_distance_matrix(
            X, self.cluster_centers_, method=self.distance_method, **self.distance_kwargs
        )
        return distances

    def _update_centroids(self, X: np.ndarray, labels: np.ndarray) -> np.ndarray:
        """Update centroids using geographic mean for custom distances."""
        new_centroids = []
        for k in range(self.n_clusters):
            mask = labels == k
            if np.any(mask):
                cluster_points = X[mask]
                centroid = np.mean(cluster_points, axis=0)
                new_centroids.append(centroid)
            else:
                new_centroids.append(self.cluster_centers_[k])
        return np.array(new_centroids)

    def fit(
        self,
        X: np.ndarray,
        y: Any = None,
        sample_weight: Any = None,
    ) -> "CustomKMeans":
        """Fit the k-means clustering with custom distance metric."""
        del y, sample_weight
        if not HAS_SKLEARN:
            return self._fit_custom_implementation(X)

        X = check_array(X, accept_sparse="csr", dtype=[np.float64, np.float32])

        super().fit(X)

        labels: np.ndarray = np.array([])
        for iteration in range(self.max_iter):
            distances = get_distance_matrix(
                X, self.cluster_centers_, method=self.distance_method, **self.distance_kwargs
            )

            labels = np.argmin(distances, axis=1)

            new_centroids = self._update_centroids(X, labels)

            if np.allclose(self.cluster_centers_, new_centroids, rtol=1e-4):
                self.cluster_centers_ = new_centroids
                self.labels_ = labels
                self.n_iter_ = iteration + 1
                break

            self.cluster_centers_ = new_centroids
        else:
            self.labels_ = labels
            self.n_iter_ = self.max_iter

        return self

    def _fit_custom_implementation(self, X: np.ndarray) -> "CustomKMeans":
        """Fallback to original implementation when sklearn is not available."""
        result = _kmeans_cluster_original(
            X, self.n_clusters, distance_method=self.distance_method, **self.distance_kwargs
        )
        self.cluster_centers_ = result["centroids"]
        self.labels_ = result["labels"]
        self.n_iter_ = result["iterations"]
        return self


def kmeans_cluster(
    data: pd.DataFrame | np.ndarray,
    n_clusters: int,
    distance_method: str = "euclidean",
    max_iter: int = 300,
    random_state: int | None = None,
    rng: np.random.Generator | None = None,
    **distance_kwargs: Any,
) -> dict[str, Any]:
    """
    K-means clustering with support for custom distance metrics.

    This function provides a unified interface that uses sklearn when available
    and falls back to the original implementation otherwise.

    Args:
        data: Input data as DataFrame or numpy array
        n_clusters: Number of clusters
        distance_method: Distance calculation method
        max_iter: Maximum iterations
        random_state: Random seed (for sklearn compatibility)
        rng: Random number generator (preferred over random_state)
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

    # Create rng from random_state if rng not provided
    if rng is None and random_state is not None:
        rng = np.random.default_rng(random_state)

    # Use sklearn-based implementation if available
    if HAS_SKLEARN and distance_method in ["euclidean", "haversine", "osrm", "google"]:
        kmeans = CustomKMeans(
            n_clusters=n_clusters,
            distance_method=distance_method,
            max_iter=max_iter,
            random_state=random_state,
            **distance_kwargs,
        )
        kmeans.fit(X)

        return {
            "labels": kmeans.labels_,
            "centroids": kmeans.cluster_centers_,
            "iterations": kmeans.n_iter_,
            "converged": kmeans.n_iter_ < max_iter,
        }

    # Fall back to original implementation
    return _kmeans_cluster_original(
        X, n_clusters, distance_method, max_iter, rng=rng, **distance_kwargs
    )


def _kmeans_cluster_original(
    data: np.ndarray,
    n_clusters: int,
    distance_method: str = "euclidean",
    max_iter: int = 300,
    rng: np.random.Generator | None = None,
    **distance_kwargs: Any,
) -> dict[str, Any]:
    """
    Original pure K-means clustering implementation (fallback).

    Args:
        data: Input data as numpy array [n, 2]
        n_clusters: Number of clusters
        distance_method: Distance calculation method
        max_iter: Maximum iterations
        rng: Random number generator for reproducibility
        **distance_kwargs: Additional arguments for distance calculation

    Returns:
        Dictionary with 'labels', 'centroids', 'iterations', 'converged'
    """
    X = data

    # Initialize centroids
    centroids = initialize_centroids(X, n_clusters, rng)
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
