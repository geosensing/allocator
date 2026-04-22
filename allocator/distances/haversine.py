"""
Haversine distance calculations for geographic coordinates.

Uses Numba JIT compilation for high performance distance matrix calculations.
"""

import numba
import numpy as np
from numba import njit

EARTH_RADIUS_M = 6_371_000.0


@njit(cache=True)
def _haversine_single(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute haversine distance between two points in meters.

    Args:
        lat1, lon1: First point coordinates in degrees
        lat2, lon2: Second point coordinates in degrees

    Returns:
        Distance in meters
    """
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))


@njit(parallel=True, cache=True)
def _haversine_matrix_jit(points_from: np.ndarray, points_to: np.ndarray) -> np.ndarray:
    """
    Compute haversine distance matrix with JIT compilation.

    Args:
        points_from: Source points array with shape [n, 2] where columns are [lon, lat]
        points_to: Destination points array with shape [m, 2] where columns are [lon, lat]

    Returns:
        Distance matrix with shape [n, m] in meters
    """
    n = len(points_from)
    m = len(points_to)
    result = np.empty((n, m), dtype=np.float64)

    for i in numba.prange(n):
        lon1, lat1 = points_from[i, 0], points_from[i, 1]
        for j in range(m):
            lon2, lat2 = points_to[j, 0], points_to[j, 1]
            result[i, j] = _haversine_single(lat1, lon1, lat2, lon2)

    return result


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
    if len(points_from) == 0:
        points_to_len = len(points_to) if points_to is not None else 0
        return np.array([]).reshape(0, points_to_len)

    if points_to is None:
        points_to = points_from

    points_from_arr = np.ascontiguousarray(points_from, dtype=np.float64)
    points_to_arr = np.ascontiguousarray(points_to, dtype=np.float64)

    return _haversine_matrix_jit(points_from_arr, points_to_arr)
