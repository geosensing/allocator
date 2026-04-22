"""
Factory module for distance calculations - main entry point.
"""

import warnings
from collections.abc import Callable

import numpy as np

from .euclidean import euclidean_distance_matrix
from .external_apis import (
    google_distance_matrix,
    google_routes_distance_matrix,
    osrm_distance_matrix,
)
from .haversine import haversine_distance_matrix

ProgressCallback = Callable[[int, int, str | None], None]


def get_distance_matrix(
    points_from: np.ndarray,
    points_to: np.ndarray | None = None,
    method: str = "euclidean",
    on_progress: ProgressCallback | None = None,
    **kwargs,
) -> np.ndarray:
    """
    Single entry point for all distance calculations.

    Args:
        points_from: Source points (numpy array with shape [n, 2] where columns are [lon, lat])
        points_to: Destination points (optional, defaults to points_from)
        method: Distance calculation method:
            - 'euclidean': Local Euclidean distance
            - 'haversine': Great-circle distance
            - 'osrm': OSRM routing service (duration in seconds)
            - 'google': Legacy Google Distance Matrix API (deprecated, use 'google_routes')
            - 'google_routes': Google Routes API (recommended)
        on_progress: Optional callback for progress reporting (current, total, message)
        **kwargs: Method-specific arguments:
            - api_key: Required for 'google' method (legacy)
            - credentials_file: Path to service account JSON for 'google_routes' method
            - osrm_base_url: Custom OSRM server URL for 'osrm' method
            - osrm_max_table_size: Chunk size for OSRM requests (default: 100)
            - duration: For Google methods, return duration instead of distance (default: True)
            - travel_mode: For 'google_routes', one of "DRIVE", "BICYCLE", "WALK",
                           "TWO_WHEELER", "TRANSIT" (default: "DRIVE")

    Returns:
        Distance matrix as numpy array with shape [len(points_from), len(points_to)]

    Raises:
        ValueError: For invalid method or missing required parameters
    """
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
            on_progress=on_progress,
        )
    elif method == "google":
        warnings.warn(
            "method='google' uses the legacy Distance Matrix API. "
            "Use method='google_routes' for the newer Routes API.",
            DeprecationWarning,
            stacklevel=2,
        )
        api_key = kwargs.get("api_key")
        if not api_key:
            raise ValueError("Google method requires api_key parameter")
        return google_distance_matrix(
            points_from,
            points_to,
            api_key=api_key,
            duration=kwargs.get("duration", True),
            on_progress=on_progress,
        )
    elif method == "google_routes":
        return google_routes_distance_matrix(
            points_from,
            points_to,
            credentials_file=kwargs.get("credentials_file"),
            duration=kwargs.get("duration", True),
            travel_mode=kwargs.get("travel_mode", "DRIVE"),
            on_progress=on_progress,
        )
    else:
        raise ValueError(
            f"Unknown distance method: {method}. "
            f"Supported methods: euclidean, haversine, osrm, google, google_routes"
        )
