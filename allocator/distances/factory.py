"""
Factory module for distance calculations - main entry point.
"""

from __future__ import annotations

import numpy as np

from .euclidean import euclidean_distance_matrix
from .external_apis import google_distance_matrix, osrm_distance_matrix
from .haversine import haversine_distance_matrix


def get_distance_matrix(
    points_from: np.ndarray,
    points_to: np.ndarray | None = None,
    method: str = "euclidean",
    **kwargs,
) -> np.ndarray:
    """
    Single entry point for all distance calculations.

    Args:
        points_from: Source points (numpy array with shape [n, 2] where columns are [lon, lat])
        points_to: Destination points (optional, defaults to points_from)
        method: Distance calculation method ('euclidean', 'haversine', 'osrm', 'google')
        **kwargs: Method-specific arguments:
            - api_key: Required for 'google' method
            - osrm_base_url: Custom OSRM server URL for 'osrm' method
            - osrm_max_table_size: Chunk size for OSRM requests (default: 100)
            - duration: For 'google' method, return duration instead of distance (default: True)

    Returns:
        Distance matrix as numpy array with shape [len(points_from), len(points_to)]

    Raises:
        ValueError: For invalid method or missing required parameters
    """
    # Handle empty arrays
    if len(points_from) == 0:
        points_to_len = len(points_to) if points_to is not None else 0
        return np.array([]).reshape(0, points_to_len)

    if method == "euclidean":
        return euclidean_distance_matrix(points_from, points_to)
    elif method == "haversine":
        return haversine_distance_matrix(points_from, points_to)
    elif method == "osrm":
        return osrm_distance_matrix(
            points_from,
            points_to,
            chunksize=kwargs.get("osrm_max_table_size", 100),
            osrm_base_url=kwargs.get("osrm_base_url"),
        )
    elif method == "google":
        api_key = kwargs.get("api_key")
        if not api_key:
            raise ValueError("Google method requires api_key parameter")
        return google_distance_matrix(
            points_from, points_to, api_key=api_key, duration=kwargs.get("duration", True)
        )
    else:
        raise ValueError(
            f"Unknown distance method: {method}. "
            f"Supported methods: euclidean, haversine, osrm, google"
        )
