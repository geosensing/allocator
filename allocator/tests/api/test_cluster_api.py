"""
Tests for the modern clustering API.
"""

import unittest
import numpy as np
import pandas as pd
from pathlib import Path

from allocator.api import cluster, kmeans, kahip
from allocator.api.types import ClusterResult


class TestClusterAPI(unittest.TestCase):
    """Test clustering API functions."""

    def setUp(self):
        """Set up test data."""
        # Modern column format
        self.modern_data = pd.DataFrame(
            {
                "longitude": [101.0, 101.1, 101.2, 101.3, 101.0, 101.1],
                "latitude": [13.0, 13.1, 13.2, 13.3, 13.0, 13.1],
                "id": range(6),
            }
        )

        # Numpy array format
        self.array_data = np.array(
            [
                [101.0, 13.0],
                [101.1, 13.1],
                [101.2, 13.2],
                [101.3, 13.3],
                [101.0, 13.0],
                [101.1, 13.1],
            ]
        )

        # List format
        self.list_data = [[101.0, 13.0], [101.1, 13.1], [101.2, 13.2], [101.3, 13.3]]

    def test_kmeans_with_modern_columns(self):
        """Test K-means with modern column names."""
        result = kmeans(self.modern_data, n_clusters=2, random_state=42)

        self.assertIsInstance(result, ClusterResult)
        self.assertEqual(len(result.labels), 6)
        self.assertEqual(len(set(result.labels)), 2)
        self.assertEqual(result.centroids.shape, (2, 2))
        self.assertTrue(result.converged)
        self.assertGreater(result.n_iter, 0)
        self.assertIsNotNone(result.inertia)
        self.assertIn("cluster", result.data.columns)
        self.assertEqual(result.metadata["method"], "kmeans")

    def test_kmeans_with_numpy_array(self):
        """Test K-means with numpy array input."""
        result = kmeans(self.array_data, n_clusters=2, random_state=42)

        self.assertIsInstance(result, ClusterResult)
        self.assertEqual(len(result.labels), 6)
        self.assertEqual(len(set(result.labels)), 2)
        self.assertTrue(result.converged)

    def test_kmeans_with_list(self):
        """Test K-means with list input."""
        result = kmeans(self.list_data, n_clusters=2, random_state=42)

        self.assertIsInstance(result, ClusterResult)
        self.assertEqual(len(result.labels), 4)
        self.assertEqual(len(set(result.labels)), 2)
        self.assertTrue(result.converged)

    def test_kmeans_different_distances(self):
        """Test K-means with different distance metrics."""
        for distance in ["euclidean", "haversine"]:
            with self.subTest(distance=distance):
                result = kmeans(self.modern_data, n_clusters=2, distance=distance, random_state=42)
                self.assertTrue(result.converged)
                self.assertEqual(result.metadata["distance"], distance)

    def test_kmeans_reproducibility(self):
        """Test that K-means is reproducible with random_state."""
        result1 = kmeans(self.modern_data, n_clusters=2, random_state=42)
        result2 = kmeans(self.modern_data, n_clusters=2, random_state=42)

        np.testing.assert_array_equal(result1.labels, result2.labels)
        np.testing.assert_array_almost_equal(result1.centroids, result2.centroids)

    def test_high_level_cluster_function(self):
        """Test the high-level cluster function."""
        result = cluster(self.modern_data, n_clusters=2, method="kmeans", random_state=42)

        self.assertIsInstance(result, ClusterResult)
        self.assertEqual(result.metadata["method"], "kmeans")

    def test_kahip_import_error_handling(self):
        """Test KaHIP handles missing dependencies gracefully."""
        with self.assertRaises(ImportError) as cm:
            kahip(self.modern_data, n_clusters=2)

        self.assertIn("kahipwrapper", str(cm.exception))

    def test_invalid_column_names(self):
        """Test error handling for invalid column names."""
        bad_data = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})

        with self.assertRaises(ValueError) as cm:
            kmeans(bad_data, n_clusters=2)

        self.assertIn("longitude", str(cm.exception))
        self.assertIn("latitude", str(cm.exception))

    def test_insufficient_data(self):
        """Test error handling for insufficient data."""
        tiny_data = pd.DataFrame({"longitude": [101.0], "latitude": [13.0]})

        # Should handle gracefully (might converge immediately or fail appropriately)
        try:
            result = kmeans(tiny_data, n_clusters=2, random_state=42)
            # If it succeeds, check that it handled the edge case
            self.assertLessEqual(len(set(result.labels)), 1)
        except (ValueError, IndexError):
            # Acceptable to fail with insufficient data
            pass

    def test_cluster_metadata(self):
        """Test that metadata is properly populated."""
        result = kmeans(
            self.modern_data, n_clusters=3, distance="haversine", max_iter=100, random_state=42
        )

        expected_keys = ["method", "distance", "n_clusters", "max_iter", "random_state"]
        for key in expected_keys:
            self.assertIn(key, result.metadata)

        self.assertEqual(result.metadata["method"], "kmeans")
        self.assertEqual(result.metadata["distance"], "haversine")
        self.assertEqual(result.metadata["n_clusters"], 3)
        self.assertEqual(result.metadata["max_iter"], 100)
        self.assertEqual(result.metadata["random_state"], 42)

    def test_file_input(self):
        """Test clustering with file input."""
        test_file = Path(__file__).parent.parent / "chonburi-roads-50.csv"
        if test_file.exists():
            result = cluster(str(test_file), n_clusters=3, random_state=42)
            self.assertIsInstance(result, ClusterResult)
            self.assertEqual(len(set(result.labels)), 3)


if __name__ == "__main__":
    unittest.main()
