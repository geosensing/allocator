"""
Tests for design effect and cluster-robust standard error computations.
"""

import unittest

import numpy as np

from allocator.stats.design_effect import compute_cluster_robust_se, compute_design_effect


class TestComputeDesignEffect(unittest.TestCase):
    """Test design effect computation."""

    def test_design_effect_no_clustering(self):
        outcomes = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        cluster_ids = np.array([0, 1, 2, 3, 4, 5, 6, 7])

        deff = compute_design_effect(outcomes, cluster_ids)
        self.assertAlmostEqual(deff, 1.0, places=1)

    def test_design_effect_high_clustering(self):
        outcomes = np.array([1.0, 1.1, 1.0, 5.0, 5.1, 5.0, 9.0, 9.1, 9.0])
        cluster_ids = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])

        deff = compute_design_effect(outcomes, cluster_ids)
        self.assertGreater(deff, 1.0)

    def test_design_effect_single_cluster(self):
        outcomes = np.array([1.0, 2.0, 3.0])
        cluster_ids = np.array([0, 0, 0])

        deff = compute_design_effect(outcomes, cluster_ids)
        self.assertEqual(deff, 1.0)

    def test_design_effect_single_point(self):
        outcomes = np.array([1.0])
        cluster_ids = np.array([0])

        deff = compute_design_effect(outcomes, cluster_ids)
        self.assertEqual(deff, 1.0)

    def test_design_effect_constant_outcomes(self):
        outcomes = np.array([5.0, 5.0, 5.0, 5.0])
        cluster_ids = np.array([0, 0, 1, 1])

        deff = compute_design_effect(outcomes, cluster_ids)
        self.assertEqual(deff, 1.0)

    def test_design_effect_always_at_least_one(self):
        outcomes = np.random.randn(100)
        cluster_ids = np.random.randint(0, 10, 100)

        deff = compute_design_effect(outcomes, cluster_ids)
        self.assertGreaterEqual(deff, 1.0)


class TestComputeClusterRobustSE(unittest.TestCase):
    """Test cluster-robust standard error computation."""

    def test_cluster_robust_se_basic(self):
        outcomes = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        cluster_ids = np.array([0, 0, 1, 1, 2, 2])

        se = compute_cluster_robust_se(outcomes, cluster_ids)
        self.assertGreater(se, 0)

    def test_cluster_robust_se_single_cluster(self):
        outcomes = np.array([1.0, 2.0, 3.0])
        cluster_ids = np.array([0, 0, 0])

        se = compute_cluster_robust_se(outcomes, cluster_ids)
        naive_se = np.std(outcomes, ddof=1) / np.sqrt(len(outcomes))
        self.assertAlmostEqual(se, naive_se, places=5)

    def test_cluster_robust_se_empty(self):
        outcomes = np.array([1.0])
        cluster_ids = np.array([0])

        se = compute_cluster_robust_se(outcomes, cluster_ids)
        self.assertEqual(se, 0.0)

    def test_cluster_robust_se_nonnegative(self):
        outcomes = np.random.randn(50)
        cluster_ids = np.random.randint(0, 5, 50)

        se = compute_cluster_robust_se(outcomes, cluster_ids)
        self.assertGreaterEqual(se, 0.0)


class TestDesignEffectPackageExport(unittest.TestCase):
    """Test that design effect functions are exported from stats module."""

    def test_import_from_stats_module(self):
        from allocator.stats import compute_cluster_robust_se, compute_design_effect

        self.assertTrue(callable(compute_design_effect))
        self.assertTrue(callable(compute_cluster_robust_se))


if __name__ == "__main__":
    unittest.main()
