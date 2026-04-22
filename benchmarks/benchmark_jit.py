#!/usr/bin/env python3
"""
Benchmark script for Numba JIT-compiled functions.

Compares performance of JIT-compiled vs pure Python implementations.
"""

import time

import numpy as np
from haversine import haversine

from allocator.distances.haversine import (
    _haversine_matrix_jit,
    _haversine_single,
    haversine_distance_matrix,
)


def haversine_distance_matrix_pure_python(
    points_from: np.ndarray, points_to: np.ndarray | None = None
) -> np.ndarray:
    """Pure Python implementation for comparison."""
    if len(points_from) == 0:
        points_to_len = len(points_to) if points_to is not None else 0
        return np.array([]).reshape(0, points_to_len)

    if points_to is None:
        points_to = points_from

    n_from, n_to = len(points_from), len(points_to)
    distances = np.zeros((n_from, n_to))

    for i, (lon_from, lat_from) in enumerate(points_from):
        for j, (lon_to, lat_to) in enumerate(points_to):
            dist_km = haversine((lat_from, lon_from), (lat_to, lon_to))
            distances[i, j] = dist_km * 1000

    return distances


def compute_route_distance_pure_python(route: list[int], distance_matrix: np.ndarray) -> float:
    """Pure Python implementation for comparison."""
    if len(route) <= 1:
        return 0.0
    total = 0.0
    for i in range(len(route) - 1):
        total += distance_matrix[route[i], route[i + 1]]
    return total


def benchmark_haversine(sizes: list[int], n_runs: int = 3) -> None:
    """Benchmark haversine distance matrix computation."""
    print("\n" + "=" * 70)
    print("HAVERSINE DISTANCE MATRIX BENCHMARK")
    print("=" * 70)

    rng = np.random.default_rng(42)

    for n in sizes:
        print(f"\n--- {n} x {n} points ({n*n:,} distances) ---")

        lons = rng.uniform(-122.5, -122.3, n)
        lats = rng.uniform(37.7, 37.9, n)
        points = np.column_stack([lons, lats])

        # Warm up JIT
        _ = haversine_distance_matrix(points[:10], points[:10])

        # Benchmark JIT version
        jit_times = []
        for _ in range(n_runs):
            start = time.perf_counter()
            result_jit = haversine_distance_matrix(points)
            jit_times.append(time.perf_counter() - start)
        jit_mean = np.mean(jit_times)

        # Benchmark pure Python version (only for smaller sizes)
        if n <= 500:
            py_times = []
            for _ in range(n_runs):
                start = time.perf_counter()
                result_py = haversine_distance_matrix_pure_python(points)
                py_times.append(time.perf_counter() - start)
            py_mean = np.mean(py_times)

            # Verify results match
            max_diff = np.abs(result_jit - result_py).max()
            print(f"  Pure Python: {py_mean*1000:.2f} ms")
            print(f"  Numba JIT:   {jit_mean*1000:.2f} ms")
            print(f"  Speedup:     {py_mean/jit_mean:.1f}x")
            print(f"  Max diff:    {max_diff:.6f} m (numerical tolerance)")
        else:
            print(f"  Numba JIT:   {jit_mean*1000:.2f} ms")
            print(f"  (Pure Python skipped for large matrices)")


def benchmark_route_distance(n_points: int, n_routes: int, n_runs: int = 100) -> None:
    """Benchmark route distance computation."""
    from allocator.core.itinerary import _compute_route_distance_jit, compute_route_distance

    print("\n" + "=" * 70)
    print("ROUTE DISTANCE COMPUTATION BENCHMARK")
    print("=" * 70)

    rng = np.random.default_rng(42)

    # Create distance matrix
    distance_matrix = rng.uniform(100, 10000, (n_points, n_points))
    np.fill_diagonal(distance_matrix, 0)

    # Create random routes
    routes = [list(rng.permutation(n_points)[:rng.integers(5, 50)]) for _ in range(n_routes)]

    print(f"\n--- {n_routes} routes, {n_points} points in matrix ---")

    # Warm up JIT
    _ = compute_route_distance(routes[0], distance_matrix)

    # Benchmark JIT version
    start = time.perf_counter()
    for _ in range(n_runs):
        for route in routes:
            _ = compute_route_distance(route, distance_matrix)
    jit_time = time.perf_counter() - start

    # Benchmark pure Python version
    start = time.perf_counter()
    for _ in range(n_runs):
        for route in routes:
            _ = compute_route_distance_pure_python(route, distance_matrix)
    py_time = time.perf_counter() - start

    print(f"  Pure Python: {py_time*1000:.2f} ms for {n_runs*n_routes} calls")
    print(f"  Numba JIT:   {jit_time*1000:.2f} ms for {n_runs*n_routes} calls")
    print(f"  Speedup:     {py_time/jit_time:.1f}x")


def main() -> None:
    print("Allocator Numba JIT Performance Benchmark")
    print("=========================================")

    # Haversine benchmarks
    benchmark_haversine([100, 250, 500, 1000, 2000])

    # Route distance benchmarks
    benchmark_route_distance(n_points=1000, n_routes=100, n_runs=100)

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
