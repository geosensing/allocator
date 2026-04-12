"""
Benchmark demonstration: Comparing itinerary generation methods.

This script demonstrates:
1. What data we test with (randomly sampled points with spatial outcomes)
2. What we expect to recover for bias (point estimates are unbiased for all methods)
3. What we expect for efficiency (greedy is most efficient, random is least)
4. Design effects (clustering inflates variance)

Key insight: With complete collection (no dropout), ALL methods give unbiased
point estimates. The differences are in:
- Efficiency: How much travel is required?
- Variance estimation: Does naive SE underestimate true SE?
"""

import time
from dataclasses import dataclass

import numpy as np
import pandas as pd

from allocator import create_itineraries
from allocator.api.itinerary import VALID_METHODS
from allocator.stats import compute_cluster_robust_se, compute_design_effect


@dataclass
class EfficiencyMetrics:
    """Efficiency metrics for a single itinerary result."""

    method: str
    total_travel: float
    n_itineraries: int
    travel_per_point: float
    size_variance: float
    size_range: tuple[int, int]
    time_ms: float


def compute_efficiency_metrics(
    method: str,
    itineraries: list[list[int]],
    distances: list[float],
    n_points: int,
    time_ms: float,
) -> EfficiencyMetrics:
    """
    Compute efficiency metrics from itinerary results.

    Args:
        method: Method name
        itineraries: List of itineraries (each is list of point indices)
        distances: Total distance for each itinerary
        n_points: Total number of points
        time_ms: Time taken in milliseconds

    Returns:
        EfficiencyMetrics dataclass
    """
    total_travel = sum(distances) if distances else 0.0
    n_itineraries = len(itineraries)
    travel_per_point = total_travel / n_points if n_points > 0 else 0.0

    sizes = [len(it) for it in itineraries]
    size_variance = float(np.var(sizes)) if sizes else 0.0
    size_range = (min(sizes), max(sizes)) if sizes else (0, 0)

    return EfficiencyMetrics(
        method=method,
        total_travel=total_travel,
        n_itineraries=n_itineraries,
        travel_per_point=travel_per_point,
        size_variance=size_variance,
        size_range=size_range,
        time_ms=time_ms,
    )


def compare_efficiency(
    points: np.ndarray | pd.DataFrame,
    methods: list[str] | None = None,
    max_distance: float | None = None,
    n_itineraries: int | None = None,
    seed: int = 42,
    **kwargs,
) -> pd.DataFrame:
    """
    Compare methods on travel efficiency.

    Args:
        points: Array of [lon, lat] coordinates or DataFrame with longitude/latitude columns
        methods: List of methods to compare (default: all applicable methods)
        max_distance: Max distance per itinerary (for greedy methods)
        n_itineraries: Number of itineraries (for partition methods)
        seed: Random seed for reproducibility
        **kwargs: Additional arguments for create_itineraries

    Returns:
        DataFrame with columns: method, total_travel, n_itineraries,
        travel_per_point, size_variance, size_min, size_max, time_ms
    """
    if methods is None:
        methods = list(VALID_METHODS)

    if isinstance(points, np.ndarray):
        df = pd.DataFrame({"longitude": points[:, 0], "latitude": points[:, 1]})
    else:
        df = points

    n_points = len(df)
    results: list[EfficiencyMetrics] = []

    for method in methods:
        needs_budget = method in ("greedy_nn", "softmax_greedy")
        needs_n = method in ("random_partition", "stratified", "round_robin", "kmeans_tsp")

        if needs_budget and max_distance is None:
            continue
        if needs_n and n_itineraries is None:
            continue

        try:
            start_time = time.perf_counter()
            result = create_itineraries(
                df,
                max_distance=max_distance,
                n_itineraries=n_itineraries,
                method=method,
                seed=seed,
                **kwargs,
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            metrics = compute_efficiency_metrics(
                method=method,
                itineraries=result.itineraries,
                distances=result.distances,
                n_points=n_points,
                time_ms=elapsed_ms,
            )
            results.append(metrics)
        except Exception:
            pass

    records = []
    for m in results:
        records.append(
            {
                "method": m.method,
                "total_travel": m.total_travel,
                "n_itineraries": m.n_itineraries,
                "travel_per_point": m.travel_per_point,
                "size_variance": m.size_variance,
                "size_min": m.size_range[0],
                "size_max": m.size_range[1],
                "time_ms": m.time_ms,
            }
        )

    return pd.DataFrame(records)


def generate_spatial_outcomes(
    points: np.ndarray,
    model: str = "spatial_gradient",
    noise_sd: float = 0.1,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """
    Generate spatially-correlated outcomes for testing.

    Args:
        points: Array of [lon, lat] coordinates
        model: Outcome model type:
            - "spatial_gradient": Y = 0.5*lon + 0.3*lat + noise
            - "random": Y = noise (no spatial pattern)
            - "clustered": Y has local clustering
            - "radial": Y depends on distance from center
        noise_sd: Standard deviation of noise
        rng: Random number generator

    Returns:
        Array of outcome values
    """
    if rng is None:
        rng = np.random.default_rng()

    n = len(points)
    noise = rng.normal(0, noise_sd, n)

    if model == "spatial_gradient":
        outcomes = 0.5 * points[:, 0] + 0.3 * points[:, 1] + noise
    elif model == "random":
        outcomes = noise
    elif model == "radial":
        centroid = points.mean(axis=0)
        distances = np.linalg.norm(points - centroid, axis=1)
        max_dist = distances.max()
        if max_dist > 0:
            outcomes = distances / max_dist + noise
        else:
            outcomes = noise
    elif model == "clustered":
        from sklearn.cluster import KMeans

        n_clusters = min(5, n)
        kmeans = KMeans(n_clusters=n_clusters, random_state=int(rng.integers(0, 2**31)))
        labels = kmeans.fit_predict(points)
        cluster_effects = rng.normal(0, 0.5, n_clusters)
        outcomes = cluster_effects[labels] + noise
    else:
        raise ValueError(f"Unknown model: {model}")

    return outcomes


def compare_design_effects(
    points: np.ndarray | pd.DataFrame,
    outcome_model: str = "spatial_gradient",
    methods: list[str] | None = None,
    n_simulations: int = 100,
    max_distance: float | None = None,
    n_itineraries: int | None = None,
    noise_sd: float = 0.1,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Compare design effects across methods.

    Args:
        points: Array of [lon, lat] coordinates or DataFrame
        outcome_model: Type of spatial outcome model
        methods: Methods to compare (default: all applicable)
        n_simulations: Number of simulation runs
        max_distance: Max distance for budget methods
        n_itineraries: Number of itineraries for partition methods
        noise_sd: Noise standard deviation for outcome generation
        seed: Random seed

    Returns:
        DataFrame with columns: method, mean_deff, std_deff, mean_cluster_se, mean_naive_se
    """
    if methods is None:
        methods = list(VALID_METHODS)

    if isinstance(points, np.ndarray):
        df = pd.DataFrame({"longitude": points[:, 0], "latitude": points[:, 1]})
        points_arr = points
    else:
        df = points
        points_arr = df[["longitude", "latitude"]].to_numpy()

    rng = np.random.default_rng(seed)

    method_results: dict[str, list[dict]] = {m: [] for m in methods}

    for _ in range(n_simulations):
        sim_seed = int(rng.integers(0, 2**31))
        outcomes = generate_spatial_outcomes(
            points_arr, model=outcome_model, noise_sd=noise_sd, rng=np.random.default_rng(sim_seed)
        )

        n = len(outcomes)
        naive_se = np.std(outcomes, ddof=1) / np.sqrt(n)

        for method in methods:
            needs_budget = method in ("greedy_nn", "softmax_greedy")
            needs_n = method in ("random_partition", "stratified", "round_robin", "kmeans_tsp")

            if needs_budget and max_distance is None:
                continue
            if needs_n and n_itineraries is None:
                continue

            try:
                result = create_itineraries(
                    df,
                    max_distance=max_distance,
                    n_itineraries=n_itineraries,
                    method=method,
                    seed=sim_seed,
                    distance="euclidean",
                )

                itinerary_ids = result.data["itinerary_id"].to_numpy()
                deff = compute_design_effect(outcomes, itinerary_ids)
                cluster_se = compute_cluster_robust_se(outcomes, itinerary_ids)

                method_results[method].append(
                    {
                        "deff": deff,
                        "cluster_se": cluster_se,
                        "naive_se": naive_se,
                    }
                )
            except Exception:
                pass

    records = []
    for method, sim_results in method_results.items():
        if not sim_results:
            continue

        deffs = [r["deff"] for r in sim_results]
        cluster_ses = [r["cluster_se"] for r in sim_results]
        naive_ses = [r["naive_se"] for r in sim_results]

        records.append(
            {
                "method": method,
                "mean_deff": np.mean(deffs),
                "std_deff": np.std(deffs),
                "mean_cluster_se": np.mean(cluster_ses),
                "mean_naive_se": np.mean(naive_ses),
                "n_simulations": len(sim_results),
            }
        )

    return pd.DataFrame(records)


def demonstrate_bias_is_zero():
    """
    Demonstrate that all methods produce unbiased point estimates.

    Key insight: Since all methods visit ALL points (no selection/dropout),
    the sample mean = population mean for any outcome.
    """
    print("=" * 70)
    print("BIAS DEMONSTRATION")
    print("=" * 70)
    print()

    n_points = 100
    n_simulations = 50
    rng = np.random.default_rng(42)

    lons = rng.uniform(-122.5, -122.0, n_points)
    lats = rng.uniform(37.5, 38.0, n_points)
    points = np.column_stack([lons, lats])
    df = pd.DataFrame({"longitude": lons, "latitude": lats})

    methods = ["greedy_nn", "random_partition", "stratified", "round_robin"]
    results = {m: [] for m in methods}

    for sim in range(n_simulations):
        sim_rng = np.random.default_rng(sim)
        outcomes = 0.5 * points[:, 0] + 0.3 * points[:, 1] + sim_rng.normal(0, 0.1, n_points)
        true_mean = outcomes.mean()

        for method in methods:
            if method in ("greedy_nn",):
                result = create_itineraries(
                    df, max_distance=20000, method=method, seed=sim, distance="haversine"
                )
            else:
                result = create_itineraries(
                    df, n_itineraries=10, method=method, seed=sim, distance="haversine"
                )

            all_points = set()
            for it in result.itineraries:
                all_points.update(it)

            collected_outcomes = outcomes[list(all_points)]
            estimate = collected_outcomes.mean()

            bias = estimate - true_mean
            results[method].append(bias)

    print("Method               Mean Bias      Std Bias")
    print("-" * 50)
    for method, biases in results.items():
        mean_bias = np.mean(biases)
        std_bias = np.std(biases)
        print(f"{method:20s} {mean_bias:+.6f}     {std_bias:.6f}")

    print()
    print("Note: All biases are effectively zero (< 1e-10) because")
    print("all methods visit ALL points - there is no selection bias.")
    print()


def demonstrate_efficiency_differences():
    """
    Demonstrate efficiency differences across methods.

    Expected results:
    - greedy_nn: Most efficient (lowest total travel)
    - softmax_greedy: Nearly as efficient as greedy
    - kmeans_tsp: Good efficiency (spatial clustering + TSP)
    - stratified: Moderate (points spread across regions)
    - round_robin: Moderate to poor
    - random_partition: Least efficient (nearby points often in different groups)
    """
    print("=" * 70)
    print("EFFICIENCY DEMONSTRATION")
    print("=" * 70)
    print()

    n_points = 100
    rng = np.random.default_rng(42)
    lons = rng.uniform(-122.5, -122.0, n_points)
    lats = rng.uniform(37.5, 38.0, n_points)
    points = np.column_stack([lons, lats])

    efficiency = compare_efficiency(
        points,
        methods=[
            "greedy_nn",
            "softmax_greedy",
            "kmeans_tsp",
            "stratified",
            "round_robin",
            "random_partition",
        ],
        max_distance=20000,
        n_itineraries=10,
        seed=42,
        distance="haversine",
    )

    greedy_row = efficiency[efficiency["method"] == "greedy_nn"]
    if len(greedy_row) > 0 and greedy_row["total_travel"].values[0] > 0:
        greedy_travel = greedy_row["total_travel"].values[0]
    else:
        greedy_travel = efficiency["total_travel"].min()
        if greedy_travel == 0:
            greedy_travel = 1.0

    print("Method               Total Travel (m)  Relative    N_Itineraries")
    print("-" * 68)
    for _, row in efficiency.iterrows():
        relative = row["total_travel"] / greedy_travel * 100 if greedy_travel > 0 else 0
        print(
            f"{row['method']:20s} {row['total_travel']:12.0f}     {relative:5.1f}%     {int(row['n_itineraries'])}"
        )

    print()
    print("Expected pattern: greedy_nn ≈ 100%, random_partition ≈ 150-200%")
    print()


def demonstrate_design_effects():
    """
    Demonstrate design effects from clustering.

    Expected results:
    - random_partition: Design effect ≈ 1.0 (no spatial correlation)
    - greedy_nn: Design effect > 1 (spatially correlated clusters)
    - stratified: Design effect ≈ 1.0-1.3 (controlled spatial spread)

    A design effect > 1 means the naive SRS standard error underestimates
    the true standard error due to within-cluster correlation.
    """
    print("=" * 70)
    print("DESIGN EFFECT DEMONSTRATION")
    print("=" * 70)
    print()

    n_points = 100
    rng = np.random.default_rng(42)
    lons = rng.uniform(-122.5, -122.0, n_points)
    lats = rng.uniform(37.5, 38.0, n_points)
    points = np.column_stack([lons, lats])
    df = pd.DataFrame({"longitude": lons, "latitude": lats})

    outcomes = generate_spatial_outcomes(points, model="spatial_gradient", noise_sd=0.1, rng=rng)

    print("Single run with spatial_gradient outcome (Y = 0.5*lon + 0.3*lat + noise):")
    print()

    methods_config = [
        ("greedy_nn", {"max_distance": 20000}),
        ("random_partition", {"n_itineraries": 10}),
        ("stratified", {"n_itineraries": 10}),
        ("round_robin", {"n_itineraries": 10}),
    ]

    print("Method               Design Effect   Interpretation")
    print("-" * 60)

    for method, kwargs in methods_config:
        result = create_itineraries(df, method=method, seed=42, distance="haversine", **kwargs)
        itinerary_ids = result.data["itinerary_id"].to_numpy()
        deff = compute_design_effect(outcomes, itinerary_ids)

        if deff < 1.2:
            interp = "Low clustering effect"
        elif deff < 2.0:
            interp = "Moderate clustering"
        else:
            interp = "High clustering effect"

        print(f"{method:20s} {deff:10.2f}       {interp}")

    print()
    print("Simulation over many random outcomes:")
    print()

    deff_results = compare_design_effects(
        points,
        outcome_model="spatial_gradient",
        methods=["greedy_nn", "random_partition", "stratified", "round_robin"],
        n_simulations=50,
        max_distance=20000,
        n_itineraries=10,
        seed=42,
    )

    print("Method               Mean DEFF    Std DEFF")
    print("-" * 45)
    for _, row in deff_results.iterrows():
        print(f"{row['method']:20s} {row['mean_deff']:8.2f}     {row['std_deff']:.2f}")

    print()


def demonstrate_when_to_use_which_method():
    """
    Summary recommendations for method selection.
    """
    print("=" * 70)
    print("METHOD SELECTION GUIDE")
    print("=" * 70)
    print()
    print("Method            Best For                           Trade-offs")
    print("-" * 70)
    print("greedy_nn         Minimizing travel distance         Higher design effect")
    print("random_partition  Theoretical baseline, unbiased SE  Poor travel efficiency")
    print("stratified        Spatial gradients in outcomes      Moderate efficiency")
    print("round_robin       Balanced itinerary sizes           Moderate efficiency")
    print("softmax_greedy    Some randomness + efficiency       Good efficiency")
    print("kmeans_tsp        Natural spatial clusters           Good efficiency")
    print()
    print("Key insight:")
    print("- For POINT ESTIMATES: All methods are unbiased (all visit all points)")
    print("- For VARIANCE ESTIMATION: Use cluster-robust SE, not naive SE")
    print("- For TRAVEL EFFICIENCY: Use greedy_nn or kmeans_tsp")
    print()


if __name__ == "__main__":
    demonstrate_bias_is_zero()
    demonstrate_efficiency_differences()
    demonstrate_design_effects()
    demonstrate_when_to_use_which_method()
