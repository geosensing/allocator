"""
Allocator v1.0: Optimally Allocate Geographically Distributed Tasks

A modern Python package for geographic task allocation, clustering, and routing optimization.

Key Features:
- Cluster geographic points into balanced groups
- Find optimal routes through locations (TSP solving)
- Assign points to closest workers/centers
- Multiple distance metrics (euclidean, haversine, OSRM, Google Maps)
- Clean API with structured results and rich metadata
- Unified CLI with beautiful terminal output

Quick Start:
    >>> import allocator
    >>> import pandas as pd
    >>>
    >>> # Create sample data
    >>> data = pd.DataFrame({
    ...     'longitude': [101.0, 101.1, 101.2],
    ...     'latitude': [13.0, 13.1, 13.2]
    ... })
    >>>
    >>> # Cluster locations
    >>> result = allocator.cluster(data, n_clusters=2)
    >>> print(result.labels)
    >>>
    >>> # Find optimal route
    >>> route = allocator.shortest_path(data, method='ortools')
    >>> print(route.route)

For more examples: https://geosensing.github.io/allocator/
"""

import logging
import sys

# Import modern API
from .api import (
    cluster,
    kmeans,
    kahip,
    shortest_path,
    tsp_christofides,
    tsp_ortools,
    tsp_osrm,
    tsp_google,
    sort_by_distance,
    assign_to_closest,
    distance_assignment,
    ClusterResult,
    RouteResult,
    SortResult,
    ComparisonResult,
)

# Import utilities for advanced users
from .distances.distance_matrix import (
    get_distance_matrix,
    euclidean_distance_matrix,
    haversine_distance_matrix,
    osrm_distance_matrix,
    google_distance_matrix,
    latlon2xy,
    xy2latlog,
)

# Import visualization functions
from .viz.plotting import plot_clusters, plot_assignments, plot_route, plot_comparison

# Version
__version__ = "1.0.0"

# Export public API
__all__ = [
    # Main functions
    "cluster",
    "shortest_path",
    "sort_by_distance",
    "assign_to_closest",
    "distance_assignment",
    # Specific methods
    "kmeans",
    "kahip",
    "tsp_christofides",
    "tsp_ortools",
    "tsp_osrm",
    "tsp_google",
    # Result types
    "ClusterResult",
    "RouteResult",
    "SortResult",
    "ComparisonResult",
    # Distance utilities
    "get_distance_matrix",
    "euclidean_distance_matrix",
    "haversine_distance_matrix",
    "osrm_distance_matrix",
    "google_distance_matrix",
    "latlon2xy",
    "xy2latlog",
    # Visualization
    "plot_clusters",
    "plot_assignments",
    "plot_route",
    "plot_comparison",
    # Logging utilities
    "setup_logging",
    "get_logger",
]


def setup_logging(level=logging.INFO):
    """
    Set up logging configuration for the allocator package.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Get root logger for allocator package
    logger = logging.getLogger("allocator")
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name):
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"allocator.{name}")


# Set up default logging
setup_logging()
