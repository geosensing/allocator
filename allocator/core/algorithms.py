"""
Pure algorithm implementations without CLI, plotting, or file I/O.
"""

from __future__ import annotations

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


class CustomKMeans(KMeans if HAS_SKLEARN else object):
    """
    Custom K-means implementation that supports geographic distance metrics.

    This class extends sklearn's KMeans to work with custom distance functions
    including haversine, OSRM, and Google Maps API distances.
    """

    def __init__(
        self,
        n_clusters=8,
        distance_method="euclidean",
        max_iter=300,
        random_state=None,
        **distance_kwargs,
    ):
        if HAS_SKLEARN:
            # Initialize sklearn KMeans with all parameters
            super().__init__(n_clusters=n_clusters, max_iter=max_iter, random_state=random_state)
        self.distance_method = distance_method
        self.distance_kwargs = distance_kwargs
        self.n_clusters = n_clusters

    def _transform(self, X):
        """Override sklearn's distance calculation to use custom metrics."""
        if not HAS_SKLEARN:
            raise ImportError(
                "sklearn is required for CustomKMeans. Install with: pip install 'allocator[algorithms]'"
            )

        # Use our custom distance factory instead of sklearn's euclidean
        distances = get_distance_matrix(
            X, self.cluster_centers_, method=self.distance_method, **self.distance_kwargs
        )
        return distances

    def _update_centroids(self, X, labels):
        """Update centroids using geographic mean for custom distances."""
        new_centroids = []
        for k in range(self.n_clusters):
            mask = labels == k
            if np.any(mask):
                # For geographic data, use simple mean of coordinates
                # This works well for most geographic clustering tasks
                cluster_points = X[mask]
                centroid = np.mean(cluster_points, axis=0)
                new_centroids.append(centroid)
            else:
                # Keep old centroid if cluster is empty
                new_centroids.append(self.cluster_centers_[k])
        return np.array(new_centroids)

    def fit(self, X, y=None, sample_weight=None):
        """Fit the k-means clustering with custom distance metric."""
        if not HAS_SKLEARN:
            # Fallback to original implementation if sklearn not available
            return self._fit_custom_implementation(X)

        X = check_array(X, accept_sparse="csr", dtype=[np.float64, np.float32])

        # Initialize using sklearn's initialization logic
        super().fit(X)

        # Now run our custom iterations
        for iteration in range(self.max_iter):
            # Calculate distances using custom metric
            distances = get_distance_matrix(
                X, self.cluster_centers_, method=self.distance_method, **self.distance_kwargs
            )

            # Assign points to nearest centroids
            labels = np.argmin(distances, axis=1)

            # Update centroids
            new_centroids = self._update_centroids(X, labels)

            # Check convergence
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

    def _fit_custom_implementation(self, X):
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
    **distance_kwargs,
) -> dict:
    """
    K-means clustering with support for custom distance metrics.

    This function provides a unified interface that uses sklearn when available
    and falls back to the original implementation otherwise.
    """
    # Convert DataFrame to numpy array if needed
    if isinstance(data, pd.DataFrame):
        if "longitude" in data.columns and "latitude" in data.columns:
            X = data[["longitude", "latitude"]].values
        else:
            raise ValueError("DataFrame must contain 'longitude' and 'latitude' columns")
    else:
        X = np.asarray(data)

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
        X, n_clusters, distance_method, max_iter, random_state, **distance_kwargs
    )


def _kmeans_cluster_original(
    data: np.ndarray,
    n_clusters: int,
    distance_method: str = "euclidean",
    max_iter: int = 300,
    random_state: int | None = None,
    **distance_kwargs,
) -> dict:
    """
    Original pure K-means clustering implementation (fallback).

    Args:
        data: Input data as numpy array [n, 2]
        n_clusters: Number of clusters
        distance_method: Distance calculation method
        max_iter: Maximum iterations
        random_state: Random seed
        **distance_kwargs: Additional arguments for distance calculation

    Returns:
        Dictionary with 'labels', 'centroids', 'iterations', 'converged'
    """
    X = data

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
