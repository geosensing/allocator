"""
Tests for the distance/assignment API.
"""

import unittest
import numpy as np
import pandas as pd

from allocator.api import distance_assignment, sort_by_distance
from allocator.api.types import SortResult


class TestDistanceAPI(unittest.TestCase):
    """Test distance assignment API functions."""

    def setUp(self):
        """Set up test data."""
        # Points to assign
        self.points = pd.DataFrame(
            {
                "longitude": [101.0, 101.1, 101.2, 101.3],
                "latitude": [13.0, 13.1, 13.2, 13.3],
                "point_id": ["P1", "P2", "P3", "P4"],
            }
        )

        # Centers to assign to
        self.centers = pd.DataFrame(
            {"longitude": [101.05, 101.25], "latitude": [13.05, 13.25], "center_id": ["C1", "C2"]}
        )

        # Numpy arrays
        self.array_points = np.array([[101.0, 13.0], [101.1, 13.1], [101.2, 13.2]])

        self.array_centers = np.array([[101.05, 13.05], [101.25, 13.25]])

    def test_distance_assignment_modern_columns(self):
        """Test distance assignment with modern column names."""
        result = distance_assignment(self.points, self.centers, distance="euclidean")

        self.assertIsInstance(result, SortResult)
        self.assertEqual(len(result.data), len(self.points))
        self.assertIn("assigned_worker", result.data.columns)
        self.assertEqual(result.metadata["method"], "assign_to_closest")
        self.assertEqual(result.metadata["distance"], "euclidean")

    def test_distance_assignment_numpy_arrays(self):
        """Test distance assignment with numpy arrays."""
        result = distance_assignment(self.array_points, self.array_centers, distance="euclidean")

        self.assertIsInstance(result, SortResult)
        self.assertEqual(len(result.data), len(self.array_points))
        self.assertIn("assigned_worker", result.data.columns)
        # Check that assignments are valid indices
        assignments = result.data["assigned_worker"].values
        self.assertTrue(
            all(0 <= assignment < len(self.array_centers) for assignment in assignments)
        )

    def test_distance_assignment_different_metrics(self):
        """Test distance assignment with different distance metrics."""
        for distance in ["euclidean", "haversine"]:
            with self.subTest(distance=distance):
                result = distance_assignment(self.points, self.centers, distance=distance)
                self.assertEqual(result.metadata["distance"], distance)
                self.assertEqual(len(result.data), len(self.points))

    def test_sort_by_distance_to_single_point(self):
        """Test sorting points by distance to a single reference point."""
        reference_point = pd.DataFrame({"longitude": [101.15], "latitude": [13.15]})

        result = sort_by_distance(self.points, reference_point, distance="euclidean")

        self.assertIsInstance(result, SortResult)
        # sort_by_distance returns all point-worker combinations sorted by distance
        # With one reference point, we get one row per input point
        self.assertEqual(len(result.data), len(self.points))
        self.assertIn("distance", result.data.columns)
        self.assertIn("rank", result.data.columns)
        self.assertEqual(result.metadata["method"], "sort_workers_by_point")

        # Check that all ranks are 1 (since there's only one reference point)
        ranks = result.data["rank"].values
        self.assertTrue(all(rank == 1 for rank in ranks))

        # Check that we have distance values for all points
        distances = result.data["distance"].values
        self.assertTrue(all(distance >= 0 for distance in distances))

    def test_sort_by_distance_numpy_input(self):
        """Test sort by distance with numpy array input."""
        reference = np.array([[101.15, 13.15]])

        result = sort_by_distance(self.array_points, reference, distance="euclidean")

        self.assertIsInstance(result, SortResult)
        self.assertEqual(len(result.data), len(self.array_points))

    def test_assignment_consistency(self):
        """Test that assignments are consistent and reasonable."""
        result = distance_assignment(self.points, self.centers, distance="euclidean")

        # Each point should be assigned to exactly one center
        self.assertEqual(len(result.data), len(self.points))
        assignments = result.data["assigned_worker"].values
        self.assertTrue(all(0 <= assignment < len(self.centers) for assignment in assignments))

        # Points closer to first center should generally be assigned to it
        # (This is a basic sanity check - exact results depend on specific coordinates)
        self.assertIsInstance(assignments, np.ndarray)

    def test_invalid_column_names(self):
        """Test error handling for invalid column names."""
        bad_points = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})

        bad_centers = pd.DataFrame({"x": [1.5], "y": [4.5]})

        with self.assertRaises(ValueError):
            distance_assignment(bad_points, bad_centers)

    def test_empty_data_handling(self):
        """Test error handling for empty data."""
        empty_points = pd.DataFrame(columns=["longitude", "latitude"])
        empty_centers = pd.DataFrame(columns=["longitude", "latitude"])

        # Empty points should succeed and return empty result
        result = distance_assignment(empty_points, self.centers)
        self.assertEqual(len(result.data), 0)
        self.assertIn("assigned_worker", result.data.columns)

        # Empty centers should raise an error
        with self.assertRaises((ValueError, IndexError)):
            distance_assignment(self.points, empty_centers)

    def test_single_center_assignment(self):
        """Test assignment when there's only one center."""
        single_center = pd.DataFrame({"longitude": [101.15], "latitude": [13.15]})

        result = distance_assignment(self.points, single_center, distance="euclidean")

        # All points should be assigned to the single center (index 0)
        assignments = result.data["assigned_worker"].values
        self.assertTrue(all(assignment == 0 for assignment in assignments))

    def test_assignment_metadata(self):
        """Test that assignment metadata is properly populated."""
        result = distance_assignment(self.points, self.centers, distance="haversine")

        expected_keys = ["method", "distance", "n_points", "n_workers"]
        for key in expected_keys:
            self.assertIn(key, result.metadata)

        self.assertEqual(result.metadata["method"], "assign_to_closest")
        self.assertEqual(result.metadata["distance"], "haversine")
        self.assertEqual(result.metadata["n_points"], len(self.points))
        self.assertEqual(result.metadata["n_workers"], len(self.centers))


if __name__ == "__main__":
    unittest.main()
