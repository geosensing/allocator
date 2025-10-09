"""
Public API for allocator package.

This module provides a modern, Pythonic interface to the allocator package.
"""

from .cluster import cluster, kmeans, kahip
from .route import shortest_path, tsp_christofides, tsp_ortools, tsp_osrm, tsp_google
from .distance import sort_by_distance, assign_to_closest, distance_assignment
from .types import ClusterResult, RouteResult, SortResult, ComparisonResult

__all__ = [
    # Main high-level functions
    "cluster",
    "shortest_path",
    "sort_by_distance",
    # Specific clustering methods
    "kmeans",
    "kahip",
    # Specific routing methods
    "tsp_christofides",
    "tsp_ortools",
    "tsp_osrm",
    "tsp_google",
    # Distance assignment methods
    "assign_to_closest",
    "distance_assignment",
    # Result types
    "ClusterResult",
    "RouteResult",
    "SortResult",
    "ComparisonResult",
]
