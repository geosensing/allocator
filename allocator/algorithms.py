"""
Pure algorithm implementations without CLI, plotting, or file I/O.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .distance_matrix import get_distance_matrix


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
    new_centroids = [points[closest == k].mean(axis=0)
                     for k in range(centroids.shape[0])]
    
    # Handle empty clusters by keeping old centroid
    for i, c in enumerate(new_centroids):
        if np.isnan(c).any():
            new_centroids[i] = centroids[i]
            
    return np.array(new_centroids)


def kmeans_cluster(data: pd.DataFrame | np.ndarray, n_clusters: int, 
                   distance_method: str = 'euclidean', max_iter: int = 300,
                   random_state: int | None = None, **distance_kwargs) -> dict:
    """
    Pure K-means clustering implementation.
    
    Args:
        data: Input data as DataFrame with start_long/start_lat or numpy array [n, 2]
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
        if 'start_long' in data.columns and 'start_lat' in data.columns:
            X = data[['start_long', 'start_lat']].values
        else:
            raise ValueError("DataFrame must contain 'start_long' and 'start_lat' columns")
    else:
        X = data
    
    # Initialize centroids
    centroids = initialize_centroids(X, n_clusters, random_state)
    old_centroids = centroids.copy()
    
    for i in range(max_iter):
        # Calculate distances and assign points to closest centroids
        distances = get_distance_matrix(centroids, X, method=distance_method, **distance_kwargs)
        labels = np.argmin(distances, axis=0)
        
        # Update centroids
        centroids = move_centroids(X, labels, centroids)
        
        # Check for convergence
        if np.allclose(old_centroids, centroids, rtol=1e-4):
            return {
                'labels': labels,
                'centroids': centroids,
                'iterations': i + 1,
                'converged': True
            }
        
        old_centroids = centroids.copy()
    
    return {
        'labels': labels,
        'centroids': centroids,
        'iterations': max_iter,
        'converged': False
    }


def sort_by_distance_assignment(data: pd.DataFrame | np.ndarray, 
                              centroids: np.ndarray, distance_method: str = 'euclidean',
                              **distance_kwargs) -> np.ndarray:
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
        if 'start_long' in data.columns and 'start_lat' in data.columns:
            X = data[['start_long', 'start_lat']].values
        else:
            raise ValueError("DataFrame must contain 'start_long' and 'start_lat' columns")
    else:
        X = data
    
    # Calculate distances and assign to closest
    distances = get_distance_matrix(X, centroids, method=distance_method, **distance_kwargs)
    labels = np.argmin(distances, axis=1)
    
    return labels


def calculate_cluster_statistics(data: pd.DataFrame, labels: np.ndarray, 
                                distance_method: str = 'euclidean',
                                **distance_kwargs) -> list[dict]:
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
    X = data[['start_long', 'start_lat']].values
    
    for cluster_id in sorted(np.unique(labels)):
        cluster_points = X[labels == cluster_id]
        n_points = len(cluster_points)
        
        if n_points <= 1:
            # Skip clusters with 0 or 1 points
            continue
            
        # Calculate distance matrix for this cluster
        distances = get_distance_matrix(cluster_points, cluster_points, 
                                       method=distance_method, **distance_kwargs)
        
        if distances is None:
            continue
            
        # Create graph and calculate MST
        G = nx.from_numpy_matrix(distances)
        T = nx.minimum_spanning_tree(G)
        
        graph_weight = int(G.size(weight='weight') / 1000)
        mst_weight = int(T.size(weight='weight') / 1000)
        
        results.append({
            'label': cluster_id,
            'n': n_points,
            'graph_weight': graph_weight,
            'mst_weight': mst_weight
        })
    
    return results