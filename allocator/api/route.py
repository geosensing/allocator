"""
Modern routing API for allocator package.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from ..io.data_handler import DataHandler
from .types import RouteResult


def shortest_path(data: str | pd.DataFrame | np.ndarray | list,
                 method: str = 'christofides',
                 distance: str = 'euclidean',
                 **kwargs) -> RouteResult:
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
    
    if method == 'christofides':
        return tsp_christofides(df, distance=distance, **kwargs)
    elif method == 'ortools':
        return tsp_ortools(df, distance=distance, **kwargs)
    elif method == 'osrm':
        return tsp_osrm(df, **kwargs)
    elif method == 'google':
        return tsp_google(df, **kwargs)
    else:
        raise ValueError(f"Unknown routing method: {method}")


def tsp_christofides(data: pd.DataFrame | np.ndarray,
                    distance: str = 'euclidean',
                    **kwargs) -> RouteResult:
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
    if 'longitude' in df.columns and 'latitude' in df.columns:
        points = df[['longitude', 'latitude']].values
    elif 'start_long' in df.columns and 'start_lat' in df.columns:
        points = df[['start_long', 'start_lat']].values
    else:
        raise ValueError("Data must contain coordinate columns")
    
    # Solve TSP
    total_distance, route = solve_tsp_christofides(points, distance_method=distance, **kwargs)
    
    # Create result DataFrame with route order
    result_df = df.iloc[route].copy()
    result_df['route_order'] = range(len(route))
    
    return RouteResult(
        route=route,
        total_distance=total_distance,
        data=result_df,
        metadata={
            'method': 'christofides',
            'distance': distance,
            'n_points': len(points)
        }
    )


def tsp_ortools(data: pd.DataFrame | np.ndarray,
               distance: str = 'euclidean',
               **kwargs) -> RouteResult:
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
    if 'longitude' in df.columns and 'latitude' in df.columns:
        points = df[['longitude', 'latitude']].values
    elif 'start_long' in df.columns and 'start_lat' in df.columns:
        points = df[['start_long', 'start_lat']].values
    else:
        raise ValueError("Data must contain coordinate columns")
    
    # Solve TSP
    total_distance, route = solve_tsp_ortools(points, distance_method=distance, **kwargs)
    
    # Create result DataFrame with route order
    result_df = df.iloc[route].copy()
    result_df['route_order'] = range(len(route))
    
    return RouteResult(
        route=route,
        total_distance=total_distance,
        data=result_df,
        metadata={
            'method': 'ortools',
            'distance': distance,
            'n_points': len(points)
        }
    )


def tsp_osrm(data: pd.DataFrame | np.ndarray,
            osrm_base_url: str | None = None,
            **kwargs) -> RouteResult:
    """
    Solve TSP using OSRM trip service.
    
    Args:
        data: Input data as DataFrame or numpy array
        osrm_base_url: Custom OSRM server URL
        **kwargs: Additional arguments
        
    Returns:
        RouteResult with route using real road network
    """
    # TODO: Extract OSRM implementation from shortest_path_osrm.py
    raise NotImplementedError("OSRM TSP will be implemented in Phase 5")


def tsp_google(data: pd.DataFrame | np.ndarray,
              api_key: str,
              **kwargs) -> RouteResult:
    """
    Solve TSP using Google Maps Directions API.
    
    Args:
        data: Input data as DataFrame or numpy array
        api_key: Google Maps API key
        **kwargs: Additional arguments
        
    Returns:
        RouteResult with route using Google's road network
    """
    # TODO: Extract Google implementation from shortest_path_gm.py
    raise NotImplementedError("Google TSP will be implemented in Phase 5")