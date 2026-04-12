"""
Design effect and cluster-robust standard error computations.

Design effects measure variance inflation due to clustering compared to
simple random sampling. These functions are useful for:
- Survey sampling with clustered designs
- Evaluating how itinerary assignment affects variance estimation
- Determining appropriate standard errors for clustered data
"""

import numpy as np


def compute_design_effect(
    outcomes: np.ndarray,
    cluster_ids: np.ndarray,
) -> float:
    """
    Compute design effect from clustered data.

    Design effect = Var(cluster) / Var(SRS)

    Values > 1 mean clustering inflates variance compared to simple random sampling.
    This is important when units within clusters are correlated.

    Args:
        outcomes: Array of outcome values for each unit
        cluster_ids: Array of cluster assignments for each unit

    Returns:
        Design effect (ratio of cluster variance to SRS variance).
        Returns 1.0 for edge cases (single cluster, constant outcomes).

    Example:
        >>> import numpy as np
        >>> outcomes = np.array([1.0, 1.1, 5.0, 5.1, 9.0, 9.1])
        >>> cluster_ids = np.array([0, 0, 1, 1, 2, 2])
        >>> deff = compute_design_effect(outcomes, cluster_ids)
        >>> deff > 1.0  # High within-cluster correlation
        True
    """
    n = len(outcomes)
    if n <= 1:
        return 1.0

    srs_var = np.var(outcomes, ddof=1) / n
    if srs_var == 0:
        return 1.0

    unique_clusters = np.unique(cluster_ids)
    n_clusters = len(unique_clusters)

    if n_clusters <= 1:
        return 1.0

    cluster_means_list = []
    cluster_sizes_list = []
    for cid in unique_clusters:
        mask = cluster_ids == cid
        cluster_means_list.append(outcomes[mask].mean())
        cluster_sizes_list.append(mask.sum())

    cluster_means = np.array(cluster_means_list)
    cluster_sizes = np.array(cluster_sizes_list)

    grand_mean = outcomes.mean()
    between_var = np.sum(cluster_sizes * (cluster_means - grand_mean) ** 2) / (n_clusters - 1)

    avg_cluster_size = n / n_clusters
    rho = 0.0
    total_var = np.var(outcomes, ddof=1)
    if total_var > 0 and avg_cluster_size > 1:
        rho = max(0, (between_var / total_var - 1 / avg_cluster_size) / (1 - 1 / avg_cluster_size))
        rho = min(rho, 1.0)

    deff = 1 + (avg_cluster_size - 1) * rho

    return max(deff, 1.0)


def compute_cluster_robust_se(
    outcomes: np.ndarray,
    cluster_ids: np.ndarray,
) -> float:
    """
    Compute cluster-robust standard error of the mean.

    When observations within clusters are correlated, the naive standard error
    (assuming independence) underestimates the true sampling variability.
    This function computes a cluster-robust SE that accounts for within-cluster
    correlation.

    Args:
        outcomes: Array of outcome values
        cluster_ids: Array of cluster assignments

    Returns:
        Cluster-robust standard error of the mean.
        Returns naive SE for single cluster, 0.0 for single observation.

    Example:
        >>> import numpy as np
        >>> outcomes = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        >>> cluster_ids = np.array([0, 0, 1, 1, 2, 2])
        >>> se = compute_cluster_robust_se(outcomes, cluster_ids)
        >>> se > 0
        True
    """
    n = len(outcomes)
    if n <= 1:
        return 0.0

    unique_clusters = np.unique(cluster_ids)
    n_clusters = len(unique_clusters)

    if n_clusters <= 1:
        return float(np.std(outcomes, ddof=1) / np.sqrt(n))

    cluster_means_list = []
    for cid in unique_clusters:
        mask = cluster_ids == cid
        cluster_means_list.append(outcomes[mask].mean())

    cluster_means = np.array(cluster_means_list)
    between_cluster_var = np.var(cluster_means, ddof=1)
    cluster_se = np.sqrt(between_cluster_var / n_clusters)

    return float(cluster_se)
