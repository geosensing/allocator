"""
Type definitions and dataclasses for allocator API.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class ClusterResult:
    """Result of clustering operation."""
    labels: np.ndarray
    centroids: np.ndarray
    n_iter: int
    inertia: float | None
    data: pd.DataFrame
    converged: bool
    metadata: dict[str, Any]


@dataclass  
class SortResult:
    """Result of sort by distance operation."""
    data: pd.DataFrame
    distance_matrix: np.ndarray | None
    metadata: dict[str, Any]


@dataclass
class RouteResult:
    """Result of shortest path operation.""" 
    route: list[int]
    total_distance: float
    data: pd.DataFrame
    metadata: dict[str, Any]


@dataclass
class ComparisonResult:
    """Result of algorithm comparison."""
    results: dict[str, ClusterResult]
    statistics: pd.DataFrame
    metadata: dict[str, Any]