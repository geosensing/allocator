"""
Tests for the budget-constrained itinerary generation API.
"""

import unittest

import numpy as np
import pandas as pd

from allocator.api import create_itineraries
from allocator.api.types import ItineraryResult
from allocator.core.itinerary import greedy_grow_itineraries


class TestItineraryAPI(unittest.TestCase):
    """Test itinerary API functions."""

    def setUp(self):
        self.test_points = pd.DataFrame(
            {
                "longitude": [101.0, 101.1, 101.2, 101.3, 101.4],
                "latitude": [13.0, 13.1, 13.0, 13.1, 13.0],
                "point_id": ["A", "B", "C", "D", "E"],
            }
        )

        self.array_points = np.array(
            [
                [101.0, 13.0],
                [101.1, 13.1],
                [101.2, 13.0],
                [101.3, 13.1],
                [101.4, 13.0],
            ]
        )

    def test_create_itineraries_with_dataframe(self):
        result = create_itineraries(
            self.test_points,
            max_distance=50000,
            distance="haversine",
            seed=42,
        )

        self.assertIsInstance(result, ItineraryResult)
        self.assertIsInstance(result.itineraries, list)
        self.assertIsInstance(result.distances, list)
        self.assertEqual(len(result.itineraries), len(result.distances))
        self.assertIn("itinerary_id", result.data.columns)
        self.assertEqual(len(result.data), len(self.test_points))

    def test_create_itineraries_with_numpy(self):
        result = create_itineraries(
            self.array_points,
            max_distance=50000,
            distance="haversine",
            seed=42,
        )

        self.assertIsInstance(result, ItineraryResult)
        self.assertEqual(len(result.itineraries), len(result.distances))

    def test_budget_enforcement(self):
        result = create_itineraries(
            self.test_points,
            max_distance=15000,
            distance="haversine",
            seed=42,
        )

        for dist in result.distances:
            self.assertLessEqual(dist, 15000)

    def test_all_points_assigned(self):
        result = create_itineraries(
            self.test_points,
            max_distance=100000,
            distance="haversine",
            seed=42,
        )

        all_points = set()
        for route in result.itineraries:
            all_points.update(route)

        self.assertEqual(all_points, set(range(len(self.test_points))))

    def test_small_budget_creates_more_itineraries(self):
        result_small = create_itineraries(
            self.test_points,
            max_distance=5000,
            distance="haversine",
            seed=42,
        )
        result_large = create_itineraries(
            self.test_points,
            max_distance=100000,
            distance="haversine",
            seed=42,
        )

        self.assertGreaterEqual(len(result_small.itineraries), len(result_large.itineraries))

    def test_start_method_first(self):
        result = create_itineraries(
            self.test_points,
            max_distance=50000,
            distance="haversine",
            start_method="first",
        )

        self.assertEqual(result.itineraries[0][0], 0)

    def test_start_method_furthest(self):
        result = create_itineraries(
            self.test_points,
            max_distance=50000,
            distance="haversine",
            start_method="furthest",
        )

        self.assertIsInstance(result, ItineraryResult)

    def test_reproducibility_with_seed(self):
        result1 = create_itineraries(
            self.test_points,
            max_distance=20000,
            distance="haversine",
            start_method="random",
            seed=42,
        )
        result2 = create_itineraries(
            self.test_points,
            max_distance=20000,
            distance="haversine",
            start_method="random",
            seed=42,
        )

        self.assertEqual(result1.itineraries, result2.itineraries)
        self.assertEqual(result1.distances, result2.distances)

    def test_empty_data(self):
        empty_data = pd.DataFrame(columns=["longitude", "latitude"])

        result = create_itineraries(
            empty_data,
            max_distance=10000,
            distance="haversine",
        )

        self.assertEqual(result.itineraries, [])
        self.assertEqual(result.distances, [])
        self.assertEqual(result.metadata["n_points"], 0)
        self.assertEqual(result.metadata["n_itineraries"], 0)

    def test_single_point(self):
        single_point = pd.DataFrame({"longitude": [101.0], "latitude": [13.0]})

        result = create_itineraries(
            single_point,
            max_distance=10000,
            distance="haversine",
        )

        self.assertEqual(len(result.itineraries), 1)
        self.assertEqual(result.itineraries[0], [0])
        self.assertEqual(result.distances[0], 0.0)

    def test_metadata_populated(self):
        result = create_itineraries(
            self.test_points,
            max_distance=30000,
            distance="haversine",
            start_method="first",
            seed=123,
        )

        expected_keys = [
            "n_points",
            "n_itineraries",
            "max_distance",
            "distance",
            "start_method",
            "seed",
            "avg_distance",
            "avg_points_per_itinerary",
        ]
        for key in expected_keys:
            self.assertIn(key, result.metadata)

        self.assertEqual(result.metadata["n_points"], len(self.test_points))
        self.assertEqual(result.metadata["max_distance"], 30000)
        self.assertEqual(result.metadata["distance"], "haversine")
        self.assertEqual(result.metadata["start_method"], "first")
        self.assertEqual(result.metadata["seed"], 123)

    def test_euclidean_distance(self):
        result = create_itineraries(
            self.test_points,
            max_distance=0.5,
            distance="euclidean",
            seed=42,
        )

        self.assertIsInstance(result, ItineraryResult)
        for dist in result.distances:
            self.assertLessEqual(dist, 0.5)


class TestGreedyGrowCore(unittest.TestCase):
    """Test core greedy growing algorithm."""

    def setUp(self):
        self.simple_matrix = np.array(
            [
                [0, 1, 2, 3],
                [1, 0, 1, 2],
                [2, 1, 0, 1],
                [3, 2, 1, 0],
            ]
        )

    def test_greedy_grow_basic(self):
        itineraries, _ = greedy_grow_itineraries(
            self.simple_matrix,
            max_distance=10,
            start_method="first",
        )

        all_points = set()
        for route in itineraries:
            all_points.update(route)

        self.assertEqual(all_points, {0, 1, 2, 3})

    def test_greedy_grow_small_budget(self):
        _, distances = greedy_grow_itineraries(
            self.simple_matrix,
            max_distance=1,
            start_method="first",
        )

        for dist in distances:
            self.assertLessEqual(dist, 1)

    def test_greedy_grow_empty_matrix(self):
        empty_matrix = np.array([]).reshape(0, 0)

        itineraries, distances = greedy_grow_itineraries(
            empty_matrix,
            max_distance=10,
            start_method="first",
        )

        self.assertEqual(itineraries, [])
        self.assertEqual(distances, [])

    def test_greedy_grow_single_point(self):
        single_matrix = np.array([[0]])

        itineraries, distances = greedy_grow_itineraries(
            single_matrix,
            max_distance=10,
            start_method="first",
        )

        self.assertEqual(len(itineraries), 1)
        self.assertEqual(itineraries[0], [0])
        self.assertEqual(distances[0], 0.0)

    def test_invalid_start_method(self):
        with self.assertRaises(ValueError) as cm:
            greedy_grow_itineraries(
                self.simple_matrix,
                max_distance=10,
                start_method="invalid",
            )

        self.assertIn("Unknown start_method", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
