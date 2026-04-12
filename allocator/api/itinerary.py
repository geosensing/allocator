"""
API for itinerary generation.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from ..core.itinerary import (
    greedy_grow_itineraries,
    kmeans_tsp_itineraries,
    random_partition_itineraries,
    round_robin_itineraries,
    softmax_greedy_itineraries,
    stratified_itineraries,
)
from ..distances import get_distance_matrix
from ..io.data_handler import DataHandler
from .types import BUDGET_METHODS, PARTITION_METHODS, VALID_METHODS, ItineraryResult


def create_itineraries(
    data: str | pd.DataFrame | np.ndarray | list[Any],
    max_distance: float | None = None,
    n_itineraries: int | None = None,
    method: str = "greedy_nn",
    distance: str = "haversine",
    start_method: str = "random",
    temperature: float = 0.1,
    n_strata: int = 4,
    optimize_routes: bool = True,
    seed: int | None = None,
    **kwargs: Any,
) -> ItineraryResult:
    """
    Create multiple itineraries from points with a distance budget per itinerary.

    Args:
        data: Input data (file path, DataFrame, numpy array, or list)
        max_distance: Maximum total distance per itinerary (in meters for haversine/osrm/google).
            Required for greedy_nn and softmax_greedy methods.
        n_itineraries: Number of itineraries to create. Required for random_partition,
            stratified, round_robin, and kmeans_tsp methods.
        method: Itinerary generation method:
            - "greedy_nn": Greedy nearest-neighbor (default, most efficient)
            - "random_partition": Random assignment (theoretical baseline)
            - "stratified": Stratified by distance from centroid
            - "round_robin": Round-robin assignment
            - "softmax_greedy": Greedy with softmax sampling
            - "kmeans_tsp": K-means clustering with TSP optimization
        distance: Distance metric ('euclidean', 'haversine', 'osrm', 'google')
        start_method: How to pick starting point for greedy methods
            - "random": Random unvisited point
            - "furthest": Point furthest from centroid of remaining points
            - "first": First available unvisited point (index order)
        temperature: Softmax temperature for softmax_greedy method (default 0.1)
        n_strata: Number of strata for stratified method (default 4)
        optimize_routes: Whether to TSP-optimize routes for partition methods (default True)
        seed: Random seed for reproducibility
        **kwargs: Additional arguments for distance calculation:
            - api_key: Required for 'google' distance
            - osrm_base_url: Custom OSRM server URL

    Returns:
        ItineraryResult containing:
            - itineraries: List of routes (each route is list of point indices)
            - distances: Total distance for each itinerary
            - data: Original DataFrame with itinerary_id column added
            - metadata: Algorithm details

    Example:
        >>> result = create_itineraries('points.csv', max_distance=20000, method='greedy_nn')
        >>> result = create_itineraries('points.csv', n_itineraries=10, method='random_partition')
    """
    if method not in VALID_METHODS:
        raise ValueError(f"Unknown method: {method}. Use one of {VALID_METHODS}")

    if method in BUDGET_METHODS and max_distance is None:
        raise ValueError(f"max_distance is required for method '{method}'")
    if method in PARTITION_METHODS and n_itineraries is None:
        raise ValueError(f"n_itineraries is required for method '{method}'")

    df = DataHandler.load_data(data)

    if len(df) == 0:
        return ItineraryResult(
            itineraries=[],
            distances=[],
            data=df.assign(itinerary_id=[]),
            metadata={
                "n_points": 0,
                "n_itineraries": 0,
                "max_distance": max_distance,
                "method": method,
                "distance": distance,
            },
        )

    points: np.ndarray = df[["longitude", "latitude"]].to_numpy()
    distance_matrix = get_distance_matrix(points, points, method=distance, **kwargs)

    rng = np.random.default_rng(seed)

    itineraries: list[list[int]]
    distances: list[float]

    if method == "greedy_nn":
        itineraries, distances = greedy_grow_itineraries(
            distance_matrix,
            max_distance=max_distance,  # type: ignore[arg-type]
            start_method=start_method,
            rng=rng,
        )
    elif method == "random_partition":
        itineraries, distances = random_partition_itineraries(
            distance_matrix,
            n_itineraries=n_itineraries,  # type: ignore[arg-type]
            optimize_routes=optimize_routes,
            rng=rng,
        )
    elif method == "stratified":
        itineraries, distances = stratified_itineraries(
            distance_matrix,
            points=points,
            n_itineraries=n_itineraries,  # type: ignore[arg-type]
            n_strata=n_strata,
            optimize_routes=optimize_routes,
            rng=rng,
        )
    elif method == "round_robin":
        itineraries, distances = round_robin_itineraries(
            distance_matrix,
            n_itineraries=n_itineraries,  # type: ignore[arg-type]
            optimize_routes=optimize_routes,
            rng=rng,
        )
    elif method == "softmax_greedy":
        itineraries, distances = softmax_greedy_itineraries(
            distance_matrix,
            max_distance=max_distance,  # type: ignore[arg-type]
            temperature=temperature,
            start_method=start_method,
            rng=rng,
        )
    else:
        itineraries, distances = kmeans_tsp_itineraries(
            distance_matrix,
            points=points,
            n_itineraries=n_itineraries,  # type: ignore[arg-type]
            max_distance=max_distance,
            rng=rng,
        )

    itinerary_ids = np.full(len(df), -1, dtype=int)
    for itinerary_idx, route in enumerate(itineraries):
        for point_idx in route:
            itinerary_ids[point_idx] = itinerary_idx

    result_df = df.copy()
    result_df["itinerary_id"] = itinerary_ids

    return ItineraryResult(
        itineraries=itineraries,
        distances=distances,
        data=result_df,
        metadata={
            "n_points": len(df),
            "n_itineraries": len(itineraries),
            "max_distance": max_distance,
            "n_itineraries_requested": n_itineraries,
            "method": method,
            "distance": distance,
            "start_method": start_method if method in BUDGET_METHODS else None,
            "temperature": temperature if method == "softmax_greedy" else None,
            "n_strata": n_strata if method == "stratified" else None,
            "optimize_routes": optimize_routes if method in PARTITION_METHODS else None,
            "seed": seed,
            "total_distance": float(sum(distances)) if distances else 0.0,
            "avg_distance": float(np.mean(distances)) if distances else 0.0,
            "avg_points_per_itinerary": (
                float(np.mean([len(it) for it in itineraries])) if itineraries else 0.0
            ),
        },
    )
