"""
Statistical utilities for clustered/itinerary data analysis.

This module provides functions for:
- Design effect computation (variance inflation due to clustering)
- Cluster-robust standard error estimation
"""

from .design_effect import compute_cluster_robust_se, compute_design_effect

__all__ = [
    "compute_cluster_robust_se",
    "compute_design_effect",
]
