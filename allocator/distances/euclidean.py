"""
Euclidean distance calculations for geographic coordinates.
"""

from __future__ import annotations

import numpy as np
import utm


def pairwise_distances(X: np.ndarray, Y: np.ndarray | None = None) -> np.ndarray:
    """Pairwise euclidean distance calculation."""
    if Y is None:
        Y = X
    return np.sqrt(((Y - X[:, np.newaxis]) ** 2).sum(axis=2))


def latlon2xy(lat: float, lon: float) -> list[float]:
    """Transform lat/lon to UTM coordinate

    Args:
        lat (float): WGS latitude
        lon (float): WGS longitude

    Returns:
        [x, y]: UTM x, y coordinate

    """
    utm_x, utm_y, _, _ = utm.from_latlon(lat, lon)

    return [utm_x, utm_y]


def xy2latlog(
    x: float, y: float, zone_number: int, zone_letter: str | None = None
) -> tuple[float, float]:
    """Transform x, y coordinate to lat/lon coordinate

    Args:
        x (float): UTM x coordinate
        y (float): UTM y coordinate
        zone_number (int): UTM zone number
        zone_letter (str, optional): UTM zone letter. Defaults to None.

    Returns:
        (lat, lon): WGS latitude, longitude

    """
    lat, lon = utm.to_latlon(x, y, zone_number, zone_letter)

    return (lat, lon)


def euclidean_distance_matrix(
    points_from: np.ndarray, points_to: np.ndarray | None = None
) -> np.ndarray:
    """
    Calculate euclidean distance matrix between two sets of lat/lon points.

    Args:
        points_from: Source points (numpy array with shape [n, 2] where columns are [lon, lat])
        points_to: Destination points (optional, defaults to points_from)

    Returns:
        Distance matrix as numpy array with shape [len(points_from), len(points_to)]
    """
    # Handle empty arrays
    if len(points_from) == 0:
        points_to_len = len(points_to) if points_to is not None else 0
        return np.array([]).reshape(0, points_to_len)

    # Convert lat/lon to UTM coordinates for accurate euclidean distance
    utm_from = np.array([latlon2xy(lat, lon) for lon, lat in points_from])

    if points_to is None:
        utm_to = utm_from
    else:
        utm_to = np.array([latlon2xy(lat, lon) for lon, lat in points_to])

    return pairwise_distances(utm_from, utm_to)
