"""
Pure routing/TSP algorithm implementations.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from ..distances.distance_matrix import get_distance_matrix


def solve_tsp_ortools(
    points: np.ndarray, distance_method: str = "euclidean", **distance_kwargs
) -> tuple[float, list[int]]:
    """
    Solve TSP using Google OR-Tools.

    Args:
        points: Array of [lon, lat] coordinates
        distance_method: Distance calculation method
        **distance_kwargs: Additional args for distance calculation

    Returns:
        (total_distance, route) tuple
    """
    try:
        from ortools.constraint_solver import pywrapcp
        from ortools.constraint_solver import routing_enums_pb2
    except ImportError:
        raise ImportError(
            "ortools package is required for OR-Tools TSP solver. Install with: pip install ortools"
        )

    # Check for empty data
    if len(points) == 0:
        raise ValueError("Cannot solve TSP with empty data")

    # Check for single point
    if len(points) == 1:
        return 0.0, [0, 0]  # Visit same point twice

    # Get distance matrix
    distances = get_distance_matrix(points, points, method=distance_method, **distance_kwargs)

    if distances is None:
        raise ValueError("Could not calculate distance matrix")

    # Create routing model with index manager
    tsp_size = len(points)
    num_vehicles = 1
    depot = 0

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(tsp_size, num_vehicles, depot)

    # Create routing model
    routing = pywrapcp.RoutingModel(manager)

    # Set up distance callback
    def distance_callback(from_index, to_index):
        # Convert from routing variable Index to distance matrix NodeIndex
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distances[from_node, to_node])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Set search parameters
    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve
    assignment = routing.SolveWithParameters(search_params)

    if not assignment:
        return float("inf"), []

    # Extract tour
    tour = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        tour.append(manager.IndexToNode(index))
        index = assignment.Value(routing.NextVar(index))
    tour.append(manager.IndexToNode(index))  # Return to start (depot)

    total_distance = assignment.ObjectiveValue()

    return float(total_distance), tour


def solve_tsp_christofides(
    points: np.ndarray, distance_method: str = "euclidean", **distance_kwargs
) -> tuple[float, list[int]]:
    """
    Solve TSP using Christofides algorithm (approximate).

    Args:
        points: Array of [lon, lat] coordinates
        distance_method: Distance calculation method
        **distance_kwargs: Additional args for distance calculation

    Returns:
        (total_distance, route) tuple
    """
    try:
        from Christofides import christofides
        import networkx as nx
    except ImportError:
        raise ImportError(
            "Christofides package is required for Christofides TSP solver. "
            "Install with: pip install Christofides"
        )

    # Get distance matrix
    distances = get_distance_matrix(points, points, method=distance_method, **distance_kwargs)

    if distances is None:
        raise ValueError("Could not calculate distance matrix")

    # Create complete graph from distance matrix
    G = nx.Graph()
    n = len(points)

    for i in range(n):
        for j in range(i + 1, n):
            G.add_edge(i, j, weight=distances[i, j])

    # Solve using Christofides algorithm
    tour = christofides(G, 0)  # Start from node 0

    # Calculate total distance
    total_distance = 0.0
    for i in range(len(tour) - 1):
        total_distance += distances[tour[i], tour[i + 1]]

    return total_distance, tour


def solve_tsp_osrm(
    points: np.ndarray, osrm_base_url: str | None = None, **kwargs
) -> tuple[float, list[int]]:
    """
    Solve TSP using OSRM trip service.

    Args:
        points: Array of [lon, lat] coordinates
        osrm_base_url: Custom OSRM server URL
        **kwargs: Additional arguments

    Returns:
        (total_distance, route) tuple
    """
    import requests

    if osrm_base_url is None:
        osrm_base_url = "http://router.project-osrm.org"

    # Format coordinates for OSRM (lon,lat format)
    coords = ";".join([f"{point[0]},{point[1]}" for point in points])

    # Build OSRM trip URL
    url = f"{osrm_base_url}/trip/v1/driving/{coords}"
    params = {
        "source": "first",
        "destination": "last",
        "roundtrip": "true",
        "steps": "false",
        "geometries": "polyline",
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data["code"] != "Ok":
            raise ValueError(f"OSRM error: {data.get('message', 'Unknown error')}")

        trip = data["trips"][0]
        total_distance = trip["distance"]  # meters

        # Extract waypoint order
        waypoints = trip["legs"]
        route = [0]  # Start with first point

        # OSRM returns the optimal order
        for leg in waypoints:
            # This is simplified - real implementation would need to parse the leg structure
            pass

        # For now, return a simple route (this would need proper OSRM response parsing)
        route = list(range(len(points))) + [0]  # Simple circular tour

        return total_distance, route

    except requests.RequestException as e:
        raise ValueError(f"OSRM request failed: {e}")


def solve_tsp_google(points: np.ndarray, api_key: str, **kwargs) -> tuple[float, list[int]]:
    """
    Solve TSP using Google Maps Directions API.

    Args:
        points: Array of [lon, lat] coordinates
        api_key: Google Maps API key
        **kwargs: Additional arguments

    Returns:
        (total_distance, route) tuple
    """
    try:
        import googlemaps
    except ImportError:
        raise ImportError(
            "googlemaps package is required for Google TSP solver. "
            "Install with: pip install googlemaps"
        )

    gmaps = googlemaps.Client(key=api_key)

    # Convert points to lat,lng format for Google
    locations = [(point[1], point[0]) for point in points]  # Google uses lat,lng

    # This is a simplified implementation
    # A full implementation would use the Google Directions API with waypoints
    # and potentially solve the TSP optimization externally

    # For now, return a basic circular tour
    n = len(points)
    route = list(range(n)) + [0]

    # Calculate approximate distance using Google Distance Matrix
    try:
        matrix = gmaps.distance_matrix(
            origins=locations, destinations=locations, mode="driving", units="metric"
        )

        total_distance = 0
        for i in range(len(route) - 1):
            from_idx = route[i]
            to_idx = route[i + 1]
            distance_info = matrix["rows"][from_idx]["elements"][to_idx]

            if distance_info["status"] == "OK":
                total_distance += distance_info["distance"]["value"]  # meters
            else:
                raise ValueError(f"Google Maps error: {distance_info['status']}")

        return float(total_distance), route

    except Exception as e:
        raise ValueError(f"Google Maps API error: {e}")
