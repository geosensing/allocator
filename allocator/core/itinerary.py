"""
Core algorithms for itinerary generation.

Provides multiple methods for creating itineraries:
- greedy_nn: Greedy nearest-neighbor (budget-driven)
- softmax_greedy: Softmax-weighted nearest-neighbor (budget-driven)
- random_partition: Random assignment (count-driven)
- stratified: Stratified by distance from centroid (count-driven)
- round_robin: Round-robin assignment (count-driven)
- kmeans_tsp: K-means clustering with TSP optimization (count-driven)
"""

import numpy as np
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def _ensure_rng(rng: np.random.Generator | None) -> np.random.Generator:
    """Return rng if provided, otherwise create a new default RNG."""
    return rng if rng is not None else np.random.default_rng()


def _validate_distance_matrix(distance_matrix: np.ndarray) -> int:
    """Validate distance matrix and return number of points. Returns 0 for empty."""
    return len(distance_matrix)


def _validate_n_itineraries(n_itineraries: int, n: int) -> int:
    """Validate and clamp n_itineraries to valid range."""
    if n_itineraries <= 0:
        raise ValueError("n_itineraries must be positive")
    return min(n_itineraries, n)


def _optimize_routes(itineraries: list[list[int]], distance_matrix: np.ndarray) -> list[list[int]]:
    """Apply TSP optimization to each route in the itinerary list."""
    return [tsp_optimize_route(it, distance_matrix) if len(it) > 2 else it for it in itineraries]


def greedy_grow_itineraries(
    distance_matrix: np.ndarray,
    max_distance: float,
    start_method: str = "random",
    rng: np.random.Generator | None = None,
) -> tuple[list[list[int]], list[float]]:
    """
    Generate multiple itineraries using greedy nearest-neighbor growth.

    Each itinerary grows by repeatedly adding the nearest unvisited point
    that doesn't exceed the distance budget.

    Args:
        distance_matrix: Square distance matrix (n x n)
        max_distance: Maximum total distance per itinerary
        start_method: How to pick starting point for each itinerary
            - "random": Random unvisited point
            - "furthest": Point furthest from centroid of remaining points
            - "first": First available unvisited point (index order)
        rng: Random number generator for reproducibility

    Returns:
        Tuple of (itineraries, distances) where:
            - itineraries: List of routes, each route is a list of point indices
            - distances: Total distance for each itinerary
    """
    n = _validate_distance_matrix(distance_matrix)
    if n == 0:
        return [], []

    rng = _ensure_rng(rng)

    remaining = set(range(n))
    itineraries: list[list[int]] = []
    distances: list[float] = []

    while remaining:
        start_idx = _pick_starting_point(remaining, distance_matrix, start_method, rng)

        itinerary = [start_idx]
        remaining.remove(start_idx)
        current_distance = 0.0

        while remaining:
            current = itinerary[-1]
            best_candidate = None
            best_dist = float("inf")

            for candidate in remaining:
                dist = distance_matrix[current, candidate]
                if current_distance + dist <= max_distance and dist < best_dist:
                    best_candidate = candidate
                    best_dist = dist

            if best_candidate is None:
                break

            itinerary.append(best_candidate)
            remaining.remove(best_candidate)
            current_distance += best_dist

        itineraries.append(itinerary)
        distances.append(current_distance)

    return itineraries, distances


def _pick_starting_point(
    remaining: set[int],
    distance_matrix: np.ndarray,
    method: str,
    rng: np.random.Generator,
) -> int:
    """Pick a starting point for a new itinerary."""
    remaining_list = list(remaining)

    if method == "random":
        return int(rng.choice(remaining_list))

    elif method == "first":
        return min(remaining_list)

    elif method == "furthest":
        if len(remaining_list) == 1:
            return remaining_list[0]

        indices = np.array(remaining_list)
        sub_matrix = distance_matrix[np.ix_(indices, indices)]
        mean_distances = sub_matrix.mean(axis=1)
        furthest_idx = np.argmax(mean_distances)
        return remaining_list[furthest_idx]

    else:
        raise ValueError(f"Unknown start_method: {method}. Use 'random', 'first', or 'furthest'.")


def compute_route_distance(route: list[int], distance_matrix: np.ndarray) -> float:
    """
    Compute total travel distance for a route.

    Args:
        route: List of point indices in visit order
        distance_matrix: Square distance matrix

    Returns:
        Total travel distance (sum of consecutive point distances)
    """
    if len(route) <= 1:
        return 0.0
    total = 0.0
    for i in range(len(route) - 1):
        total += distance_matrix[route[i], route[i + 1]]
    return total


def tsp_optimize_route(
    route: list[int],
    distance_matrix: np.ndarray,
) -> list[int]:
    """
    Optimize route order using OR-Tools TSP solver.

    Args:
        route: List of point indices to optimize
        distance_matrix: Full distance matrix (indices must be valid)

    Returns:
        Reordered route with same points in optimal order
    """
    if len(route) <= 2:
        return route

    n = len(route)
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[route[from_node], route[to_node]])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(search_params)
    if not solution:
        return route

    optimized = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        optimized.append(route[manager.IndexToNode(index)])
        index = solution.Value(routing.NextVar(index))

    return optimized


def random_partition_itineraries(
    distance_matrix: np.ndarray,
    n_itineraries: int,
    optimize_routes: bool = True,
    rng: np.random.Generator | None = None,
) -> tuple[list[list[int]], list[float]]:
    """
    Randomly partition points into n_itineraries groups.

    1. Shuffle point indices
    2. Split into n equal groups
    3. (Optional) TSP-optimize within each group

    Args:
        distance_matrix: Square distance matrix (n x n)
        n_itineraries: Number of itineraries to create
        optimize_routes: Whether to TSP-optimize routes within each group
        rng: Random number generator for reproducibility

    Returns:
        Tuple of (itineraries, distances)
    """
    n = _validate_distance_matrix(distance_matrix)
    if n == 0:
        return [], []

    rng = _ensure_rng(rng)
    n_itineraries = _validate_n_itineraries(n_itineraries, n)

    indices = rng.permutation(n)
    group_size = n // n_itineraries

    itineraries: list[list[int]] = []
    for i in range(n_itineraries):
        start = i * group_size
        end = n if i == n_itineraries - 1 else start + group_size
        itineraries.append(list(indices[start:end]))

    if optimize_routes:
        itineraries = _optimize_routes(itineraries, distance_matrix)

    distances = [compute_route_distance(it, distance_matrix) for it in itineraries]
    return itineraries, distances


def stratified_itineraries(
    distance_matrix: np.ndarray,
    points: np.ndarray,
    n_itineraries: int,
    n_strata: int = 4,
    optimize_routes: bool = True,
    rng: np.random.Generator | None = None,
) -> tuple[list[list[int]], list[float]]:
    """
    Stratify by distance from centroid, random within strata.

    Each itinerary gets points from all spatial regions.

    Args:
        distance_matrix: Square distance matrix (n x n)
        points: Array of [lon, lat] coordinates
        n_itineraries: Number of itineraries to create
        n_strata: Number of distance strata (default 4: quartiles)
        optimize_routes: Whether to TSP-optimize routes
        rng: Random number generator for reproducibility

    Returns:
        Tuple of (itineraries, distances)
    """
    n = _validate_distance_matrix(distance_matrix)
    if n == 0:
        return [], []

    rng = _ensure_rng(rng)
    n_itineraries = _validate_n_itineraries(n_itineraries, n)

    centroid = points.mean(axis=0)
    distances_to_center = np.linalg.norm(points - centroid, axis=1)

    strata_bounds = np.percentile(distances_to_center, np.linspace(0, 100, n_strata + 1))
    strata_bounds[-1] += 1e-10

    itineraries: list[list[int]] = [[] for _ in range(n_itineraries)]

    for stratum_idx in range(n_strata):
        in_stratum = np.where(
            (distances_to_center >= strata_bounds[stratum_idx])
            & (distances_to_center < strata_bounds[stratum_idx + 1])
        )[0]

        shuffled = rng.permutation(in_stratum)
        for i, point_idx in enumerate(shuffled):
            itineraries[i % n_itineraries].append(int(point_idx))

    if optimize_routes:
        itineraries = _optimize_routes(itineraries, distance_matrix)

    distances = [compute_route_distance(it, distance_matrix) for it in itineraries]
    return itineraries, distances


def round_robin_itineraries(
    distance_matrix: np.ndarray,
    n_itineraries: int,
    optimize_routes: bool = True,
    rng: np.random.Generator | None = None,
) -> tuple[list[list[int]], list[float]]:
    """
    Round-robin assignment of shuffled points.

    1. Shuffle all points randomly
    2. Assign: point[0]->itinerary[0], point[1]->itinerary[1], ...
    3. TSP-optimize routes

    Args:
        distance_matrix: Square distance matrix (n x n)
        n_itineraries: Number of itineraries to create
        optimize_routes: Whether to TSP-optimize routes
        rng: Random number generator for reproducibility

    Returns:
        Tuple of (itineraries, distances)
    """
    n = _validate_distance_matrix(distance_matrix)
    if n == 0:
        return [], []

    rng = _ensure_rng(rng)
    n_itineraries = _validate_n_itineraries(n_itineraries, n)

    indices = rng.permutation(n)

    itineraries: list[list[int]] = [[] for _ in range(n_itineraries)]
    for i, point_idx in enumerate(indices):
        itineraries[i % n_itineraries].append(int(point_idx))

    if optimize_routes:
        itineraries = _optimize_routes(itineraries, distance_matrix)

    distances = [compute_route_distance(it, distance_matrix) for it in itineraries]
    return itineraries, distances


def softmax_greedy_itineraries(
    distance_matrix: np.ndarray,
    max_distance: float,
    temperature: float = 0.1,
    start_method: str = "random",
    rng: np.random.Generator | None = None,
) -> tuple[list[list[int]], list[float]]:
    """
    Like greedy, but sample next point with softmax probabilities.

    Lower temperature -> more like pure greedy
    Higher temperature -> more random

    Args:
        distance_matrix: Square distance matrix (n x n)
        max_distance: Maximum total distance per itinerary
        temperature: Softmax temperature (default 0.1)
        start_method: How to pick starting point ("random", "first", "furthest")
        rng: Random number generator for reproducibility

    Returns:
        Tuple of (itineraries, distances)
    """
    n = _validate_distance_matrix(distance_matrix)
    if n == 0:
        return [], []

    rng = _ensure_rng(rng)

    remaining = set(range(n))
    itineraries: list[list[int]] = []
    distances: list[float] = []

    while remaining:
        start_idx = _pick_starting_point(remaining, distance_matrix, start_method, rng)

        itinerary = [start_idx]
        remaining.remove(start_idx)
        current_distance = 0.0

        while remaining:
            current = itinerary[-1]

            candidates = []
            candidate_dists = []
            for candidate in remaining:
                dist = distance_matrix[current, candidate]
                if current_distance + dist <= max_distance:
                    candidates.append(candidate)
                    candidate_dists.append(dist)

            if not candidates:
                break

            candidate_dists_arr = np.array(candidate_dists)
            max_dist = candidate_dists_arr.max()
            if max_dist > 0:
                normalized = candidate_dists_arr / max_dist
            else:
                normalized = candidate_dists_arr

            weights = np.exp(-normalized / temperature)
            weights = weights / weights.sum()

            next_idx = rng.choice(len(candidates), p=weights)
            next_point = candidates[next_idx]
            next_dist = candidate_dists[next_idx]

            itinerary.append(next_point)
            remaining.remove(next_point)
            current_distance += next_dist

        itineraries.append(itinerary)
        distances.append(current_distance)

    return itineraries, distances


def kmeans_tsp_itineraries(
    distance_matrix: np.ndarray,
    points: np.ndarray,
    n_itineraries: int,
    max_distance: float | None = None,
    rng: np.random.Generator | None = None,
) -> tuple[list[list[int]], list[float]]:
    """
    K-means cluster points, then TSP-optimize within each cluster.

    If a cluster exceeds budget, it's split randomly.

    Args:
        distance_matrix: Square distance matrix (n x n)
        points: Array of [lon, lat] coordinates
        n_itineraries: Number of clusters/itineraries
        max_distance: Optional max distance per itinerary (splits clusters if exceeded)
        rng: Random number generator for reproducibility

    Returns:
        Tuple of (itineraries, distances)
    """
    from sklearn.cluster import KMeans

    n = _validate_distance_matrix(distance_matrix)
    if n == 0:
        return [], []

    rng = _ensure_rng(rng)
    n_itineraries = _validate_n_itineraries(n_itineraries, n)

    kmeans = KMeans(n_clusters=n_itineraries, random_state=int(rng.integers(0, 2**31)))
    labels = kmeans.fit_predict(points)

    itineraries: list[list[int]] = []
    for cluster_id in range(n_itineraries):
        cluster_indices = list(np.where(labels == cluster_id)[0])
        if len(cluster_indices) == 0:
            continue

        if len(cluster_indices) > 2:
            cluster_indices = tsp_optimize_route(cluster_indices, distance_matrix)

        if max_distance is not None:
            route_dist = compute_route_distance(cluster_indices, distance_matrix)
            if route_dist > max_distance:
                rng.shuffle(cluster_indices)
                mid = len(cluster_indices) // 2
                part1 = cluster_indices[:mid]
                part2 = cluster_indices[mid:]
                part1, part2 = _optimize_routes([part1, part2], distance_matrix)
                itineraries.extend([part1, part2])
                continue

        itineraries.append(cluster_indices)

    distances = [compute_route_distance(it, distance_matrix) for it in itineraries]
    return itineraries, distances
