"""
Modern distance-based assignment API for allocator package.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from ..core.algorithms import sort_by_distance_assignment
from ..io.data_handler import DataHandler
from .types import SortResult


def sort_by_distance(
    points: str | pd.DataFrame | np.ndarray | list,
    workers: str | pd.DataFrame | np.ndarray | list,
    by_worker: bool = False,
    distance: str = "euclidean",
    **kwargs,
) -> SortResult:
    """
    Sort points by distance to workers or vice versa.

    Args:
        points: Geographic points to assign (file path, DataFrame, numpy array, or list)
        workers: Worker/centroid locations (file path, DataFrame, numpy array, or list)
        by_worker: If True, sort points by worker; if False, sort workers by point
        distance: Distance metric ('euclidean', 'haversine', 'osrm', 'google')
        **kwargs: Additional distance-specific arguments

    Returns:
        SortResult with assignments and distance information

    Example:
        >>> result = sort_by_distance('points.csv', 'workers.csv')
        >>> print(result.data)  # Points with worker assignments
    """
    # Load and standardize data
    points_df = DataHandler.load_data(points)
    workers_df = DataHandler.load_data(workers)

    if by_worker:
        return _sort_points_by_worker(points_df, workers_df, distance=distance, **kwargs)
    else:
        return _sort_workers_by_point(points_df, workers_df, distance=distance, **kwargs)


def _sort_workers_by_point(
    points_df: pd.DataFrame, workers_df: pd.DataFrame, distance: str = "euclidean", **kwargs
) -> SortResult:
    """Sort workers by distance to each point (default behavior)."""
    from ..distances.distance_matrix import get_distance_matrix

    # Extract coordinates
    points_coords = _extract_coordinates(points_df)
    workers_coords = _extract_coordinates(workers_df)

    # Calculate distance matrix
    distance_matrix = get_distance_matrix(points_coords, workers_coords, method=distance, **kwargs)

    # Create result DataFrame
    result_data = []
    for i, (_, point_row) in enumerate(points_df.iterrows()):
        point_distances = distance_matrix[i, :]
        sorted_worker_indices = np.argsort(point_distances)

        for rank, worker_idx in enumerate(sorted_worker_indices):
            worker_row = workers_df.iloc[worker_idx]
            result_row = {
                "point_id": i,
                "worker_id": worker_idx,
                "rank": rank + 1,
                "distance": point_distances[worker_idx],
            }
            # Add point data
            for col in points_df.columns:
                result_row[f"point_{col}"] = point_row[col]
            # Add worker data
            for col in workers_df.columns:
                result_row[f"worker_{col}"] = worker_row[col]
            result_data.append(result_row)

    result_df = pd.DataFrame(result_data)

    return SortResult(
        data=result_df,
        distance_matrix=distance_matrix,
        metadata={
            "method": "sort_workers_by_point",
            "distance": distance,
            "n_points": len(points_df),
            "n_workers": len(workers_df),
        },
    )


def _sort_points_by_worker(
    points_df: pd.DataFrame, workers_df: pd.DataFrame, distance: str = "euclidean", **kwargs
) -> SortResult:
    """Sort points by distance to each worker."""
    from ..distances.distance_matrix import get_distance_matrix

    # Extract coordinates
    points_coords = _extract_coordinates(points_df)
    workers_coords = _extract_coordinates(workers_df)

    # Calculate distance matrix
    distance_matrix = get_distance_matrix(points_coords, workers_coords, method=distance, **kwargs)

    # Create result DataFrame
    result_data = []
    for j, (_, worker_row) in enumerate(workers_df.iterrows()):
        worker_distances = distance_matrix[:, j]
        sorted_point_indices = np.argsort(worker_distances)

        for rank, point_idx in enumerate(sorted_point_indices):
            point_row = points_df.iloc[point_idx]
            result_row = {
                "worker_id": j,
                "point_id": point_idx,
                "rank": rank + 1,
                "distance": worker_distances[point_idx],
            }
            # Add worker data
            for col in workers_df.columns:
                result_row[f"worker_{col}"] = worker_row[col]
            # Add point data
            for col in points_df.columns:
                result_row[f"point_{col}"] = point_row[col]
            result_data.append(result_row)

    result_df = pd.DataFrame(result_data)

    return SortResult(
        data=result_df,
        distance_matrix=distance_matrix,
        metadata={
            "method": "sort_points_by_worker",
            "distance": distance,
            "n_points": len(points_df),
            "n_workers": len(workers_df),
        },
    )


def distance_assignment(
    points: str | pd.DataFrame | np.ndarray | list,
    workers: str | pd.DataFrame | np.ndarray | list,
    distance: str = "euclidean",
    **kwargs,
) -> SortResult:
    """
    Assign each point to its closest worker (alias for assign_to_closest).

    Args:
        points: Geographic points to assign
        workers: Worker/centroid locations
        distance: Distance metric
        **kwargs: Additional distance-specific arguments

    Returns:
        SortResult with point assignments
    """
    return assign_to_closest(points, workers, distance=distance, **kwargs)


def assign_to_closest(
    points: str | pd.DataFrame | np.ndarray | list,
    workers: str | pd.DataFrame | np.ndarray | list,
    distance: str = "euclidean",
    **kwargs,
) -> SortResult:
    """
    Assign each point to its closest worker.

    Args:
        points: Geographic points to assign
        workers: Worker/centroid locations
        distance: Distance metric
        **kwargs: Additional distance-specific arguments

    Returns:
        SortResult with point assignments
    """
    # Load and standardize data
    points_df = DataHandler.load_data(points)
    workers_df = DataHandler.load_data(workers)

    # Extract coordinates
    workers_coords = _extract_coordinates(workers_df)

    # Get assignments using core algorithm
    labels = sort_by_distance_assignment(
        points_df, workers_coords, distance_method=distance, **kwargs
    )

    # Create result DataFrame
    result_df = points_df.copy()
    result_df["assigned_worker"] = labels

    # Add worker info
    for i, label in enumerate(labels):
        worker_row = workers_df.iloc[label]
        for col in workers_df.columns:
            result_df.loc[i, f"worker_{col}"] = worker_row[col]

    return SortResult(
        data=result_df,
        distance_matrix=None,
        metadata={
            "method": "assign_to_closest",
            "distance": distance,
            "n_points": len(points_df),
            "n_workers": len(workers_df),
        },
    )


def _extract_coordinates(df: pd.DataFrame) -> np.ndarray:
    """Extract longitude/latitude coordinates from DataFrame."""
    if "longitude" in df.columns and "latitude" in df.columns:
        return df[["longitude", "latitude"]].values
    else:
        raise ValueError("DataFrame must contain 'longitude' and 'latitude' columns")
