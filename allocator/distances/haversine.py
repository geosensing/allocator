"""
Haversine distance calculations for geographic coordinates.
"""

from __future__ import annotations

import numpy as np
from haversine import haversine


def haversine_distance_matrix(
    points_from: np.ndarray, points_to: np.ndarray | None = None
) -> np.ndarray:
    """
    Calculate haversine distance matrix between two sets of lat/lon points.

    Args:
        points_from: Source points (numpy array with shape [n, 2] where columns are [lon, lat])
        points_to: Destination points (optional, defaults to points_from)

    Returns:
        Distance matrix as numpy array with shape [len(points_from), len(points_to)]
        Values are in meters.
    """
    # Handle empty arrays
    if len(points_from) == 0:
        points_to_len = len(points_to) if points_to is not None else 0
        return np.array([]).reshape(0, points_to_len)

    if points_to is None:
        points_to = points_from

    # Calculate haversine distances (returned in km, convert to meters)
    n_from, n_to = len(points_from), len(points_to)
    distances = np.zeros((n_from, n_to))

    for i, (lon_from, lat_from) in enumerate(points_from):
        for j, (lon_to, lat_to) in enumerate(points_to):
            # haversine expects (lat, lon) order and returns km
            dist_km = haversine((lat_from, lon_from), (lat_to, lon_to))
            distances[i, j] = dist_km * 1000  # Convert to meters

    return distances
