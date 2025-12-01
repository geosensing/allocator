"""
Modern routing API for allocator package.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..io.data_handler import DataHandler
from .types import RouteResult


def _solve_tsp_nearest_neighbor(distance_matrix: np.ndarray) -> tuple[float, list[int]]:
    """
    Solve TSP using nearest neighbor heuristic.

    Args:
        distance_matrix: Symmetric distance matrix

    Returns:
        Tuple of (total_distance, route)
    """
    n = len(distance_matrix)
    if n == 0:
        return 0.0, []
    if n == 1:
        return 0.0, [0]

    # Start from node 0
    unvisited = set(range(1, n))
    route = [0]
    current = 0
    total_distance = 0.0

    while unvisited:
        # Find nearest unvisited node
        nearest = min(unvisited, key=lambda x: distance_matrix[current, x])
        total_distance += distance_matrix[current, nearest]
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    # Return to start
    total_distance += distance_matrix[current, 0]
    route.append(0)

    return total_distance, route


def shortest_path(
    data: str | pd.DataFrame | np.ndarray | list,
    method: str = "christofides",
    distance: str = "euclidean",
    **kwargs,
) -> RouteResult:
    """
    Find shortest path through geographic points (TSP).

    Args:
        data: Input data (file path, DataFrame, numpy array, or list)
        method: TSP solving method ('christofides', 'ortools', 'osrm', 'google')
        distance: Distance metric ('euclidean', 'haversine', 'osrm', 'google')
        **kwargs: Additional method-specific arguments

    Returns:
        RouteResult with optimal route and total distance

    Example:
        >>> result = shortest_path('points.csv', method='ortools')
        >>> print(result.route)  # Optimal visiting order
        >>> print(result.total_distance)  # Total route distance
    """
    # Load and standardize data
    df = DataHandler.load_data(data)

    if method == "christofides":
        return tsp_christofides(df, distance=distance, **kwargs)
    elif method == "ortools":
        return tsp_ortools(df, distance=distance, **kwargs)
    elif method == "osrm":
        return tsp_osrm(df, **kwargs)
    elif method == "google":
        return tsp_google(df, **kwargs)
    else:
        raise ValueError(f"Unknown routing method: {method}")


def tsp_christofides(
    data: pd.DataFrame | np.ndarray, distance: str = "euclidean", **kwargs
) -> RouteResult:
    """
    Solve TSP using Christofides algorithm (approximate).

    Args:
        data: Input data as DataFrame or numpy array
        distance: Distance metric
        **kwargs: Additional arguments

    Returns:
        RouteResult with approximate optimal route
    """
    from ..core.routing import solve_tsp_christofides

    # Load and standardize data
    df = DataHandler.load_data(data)

    # Extract coordinates
    if "longitude" in df.columns and "latitude" in df.columns:
        points = df[["longitude", "latitude"]].values
    else:
        raise ValueError("Data must contain 'longitude' and 'latitude' columns")

    # Solve TSP
    total_distance, route = solve_tsp_christofides(points, distance_method=distance, **kwargs)

    # Create result DataFrame with route order
    result_df = df.iloc[route].copy()
    result_df["route_order"] = range(len(route))

    return RouteResult(
        route=route,
        total_distance=total_distance,
        data=result_df,
        metadata={"method": "christofides", "distance": distance, "n_points": len(points)},
    )


def tsp_ortools(
    data: pd.DataFrame | np.ndarray, distance: str = "euclidean", **kwargs
) -> RouteResult:
    """
    Solve TSP using Google OR-Tools (exact for small problems).

    Args:
        data: Input data as DataFrame or numpy array
        distance: Distance metric
        **kwargs: Additional arguments

    Returns:
        RouteResult with optimal route
    """
    from ..core.routing import solve_tsp_ortools

    # Load and standardize data
    df = DataHandler.load_data(data)

    # Extract coordinates
    if "longitude" in df.columns and "latitude" in df.columns:
        points = df[["longitude", "latitude"]].values
    else:
        raise ValueError("Data must contain 'longitude' and 'latitude' columns")

    # Solve TSP
    total_distance, route = solve_tsp_ortools(points, distance_method=distance, **kwargs)

    # Create result DataFrame with route order
    result_df = df.iloc[route].copy()
    result_df["route_order"] = range(len(route))

    return RouteResult(
        route=route,
        total_distance=total_distance,
        data=result_df,
        metadata={"method": "ortools", "distance": distance, "n_points": len(points)},
    )


def tsp_osrm(
    data: pd.DataFrame | np.ndarray, osrm_base_url: str | None = None, **kwargs
) -> RouteResult:
    """
    Solve TSP using OSRM distance matrix and nearest neighbor heuristic.

    Args:
        data: Input data as DataFrame or numpy array
        osrm_base_url: Custom OSRM server URL
        **kwargs: Additional arguments

    Returns:
        RouteResult with route using real road network
    """
    points = DataHandler.load_data(data)

    if len(points) == 0:
        raise ValueError("Cannot solve TSP with empty data")
    if len(points) == 1:
        route = [0]
        total_distance = 0.0
    else:
        # Use OSRM distance matrix to solve TSP with nearest neighbor heuristic
        from ..distances import osrm_distance_matrix

        distances = osrm_distance_matrix(
            points[["longitude", "latitude"]].values, osrm_base_url=osrm_base_url
        )

        total_distance, route = _solve_tsp_nearest_neighbor(distances)

    # Create result DataFrame
    result_df = points.copy()
    result_df["route_order"] = [route.index(i) if i in route else -1 for i in range(len(points))]

    return RouteResult(
        route=route,
        total_distance=total_distance,
        data=result_df,
        metadata={"method": "osrm", "osrm_base_url": osrm_base_url, "n_points": len(points)},
    )


def tsp_google(data: pd.DataFrame | np.ndarray, api_key: str, **kwargs) -> RouteResult:
    """
    Solve TSP using Google Maps distance matrix and nearest neighbor heuristic.

    Args:
        data: Input data as DataFrame or numpy array
        api_key: Google Maps API key
        **kwargs: Additional arguments

    Returns:
        RouteResult with route using Google's road network
    """
    points = DataHandler.load_data(data)

    if len(points) == 0:
        raise ValueError("Cannot solve TSP with empty data")
    if len(points) == 1:
        route = [0]
        total_distance = 0.0
    else:
        # Use Google Maps distance matrix to solve TSP with nearest neighbor heuristic
        from ..distances import google_distance_matrix

        distances = google_distance_matrix(
            points[["longitude", "latitude"]].values,
            api_key=api_key,
            duration=False,  # Get distance, not duration
        )

        total_distance, route = _solve_tsp_nearest_neighbor(distances)

    # Create result DataFrame
    result_df = points.copy()
    result_df["route_order"] = [route.index(i) if i in route else -1 for i in range(len(points))]

    return RouteResult(
        route=route,
        total_distance=total_distance,
        data=result_df,
        metadata={
            "method": "google",
            "api_key": "***" if api_key else None,  # Don't log actual API key
            "n_points": len(points),
        },
    )
