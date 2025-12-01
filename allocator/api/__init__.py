"""
Public API for allocator package.

This module provides a modern, Pythonic interface to the allocator package.
"""

from .cluster import cluster, kmeans
from .distance import assign_to_closest, distance_assignment, sort_by_distance
from .route import shortest_path, tsp_christofides, tsp_google, tsp_ortools, tsp_osrm
from .types import ClusterResult, ComparisonResult, RouteResult, SortResult

__all__ = [
    # Result types
    "ClusterResult",
    "ComparisonResult",
    "RouteResult",
    "SortResult",
    # Distance assignment methods
    "assign_to_closest",
    # Main high-level functions
    "cluster",
    "distance_assignment",
    # Specific clustering methods
    "kmeans",
    "shortest_path",
    "sort_by_distance",
    # Specific routing methods
    "tsp_christofides",
    "tsp_google",
    "tsp_ortools",
    "tsp_osrm",
]
