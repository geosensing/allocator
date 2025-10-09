"""
Allocator package for clustering and routing optimization.

Modern Pythonic API for geographic task allocation, clustering, and routing.
"""

import logging
import sys

# Import modern API
from .api import (
    cluster, kmeans, kahip,
    shortest_path, tsp_christofides, tsp_ortools, tsp_osrm, tsp_google,
    sort_by_distance, assign_to_closest,
    ClusterResult, RouteResult, SortResult, ComparisonResult
)

# Version
__version__ = "1.0.0"

# Export public API
__all__ = [
    # Main functions
    'cluster',
    'shortest_path', 
    'sort_by_distance',
    'assign_to_closest',
    
    # Specific methods
    'kmeans',
    'kahip',
    'tsp_christofides',
    'tsp_ortools', 
    'tsp_osrm',
    'tsp_google',
    
    # Result types
    'ClusterResult',
    'RouteResult',
    'SortResult', 
    'ComparisonResult',
    
    # Utilities
    'setup_logging',
    'get_logger',
]


def setup_logging(level=logging.INFO):
    """
    Set up logging configuration for the allocator package.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Get root logger for allocator package
    logger = logging.getLogger('allocator')
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
    return logging.getLogger(f'allocator.{name}')


# Set up default logging
setup_logging()
