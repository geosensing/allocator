"""
Tests for the modern routing API.
"""

import itertools
import unittest

import numpy as np
import pandas as pd

from allocator.api import shortest_path, tsp_christofides, tsp_ortools
from allocator.api.types import RouteResult
from allocator.distances import get_distance_matrix


class TestRouteAPI(unittest.TestCase):
    """Test routing API functions."""

    def setUp(self):
        """Set up test data."""
        # Small TSP instance for testing
        self.test_points = pd.DataFrame(
            {
                "longitude": [101.0, 101.1, 101.2, 101.1],
                "latitude": [13.0, 13.1, 13.0, 12.9],
                "point_id": ["A", "B", "C", "D"],
            }
        )

        # Numpy array format
        self.array_points = np.array([[101.0, 13.0], [101.1, 13.1], [101.2, 13.0], [101.1, 12.9]])

        # List format
        self.list_points = [[101.0, 13.0], [101.1, 13.1], [101.2, 13.0]]

    def test_tsp_ortools_with_dataframe(self):
        """Test OR-Tools TSP with DataFrame input."""
        try:
            result = tsp_ortools(self.test_points, distance="euclidean")

            self.assertIsInstance(result, RouteResult)
            self.assertIsInstance(result.route, list)
            self.assertGreater(len(result.route), len(self.test_points))  # Includes return to start
            self.assertIsInstance(result.total_distance, float)
            self.assertGreater(result.total_distance, 0)
            self.assertEqual(len(result.data), len(result.route))
            self.assertIn("route_order", result.data.columns)
            self.assertEqual(result.metadata["method"], "ortools")

            # Check that route starts and ends at same point (TSP property)
            self.assertEqual(result.route[0], result.route[-1])

        except ImportError:
            self.skipTest("OR-Tools not available")

    def test_tsp_ortools_with_numpy(self):
        """Test OR-Tools TSP with numpy array input."""
        try:
            result = tsp_ortools(self.array_points, distance="euclidean")

            self.assertIsInstance(result, RouteResult)
            self.assertGreater(result.total_distance, 0)

        except ImportError:
            self.skipTest("OR-Tools not available")

    def test_tsp_ortools_with_list(self):
        """Test OR-Tools TSP with list input."""
        try:
            result = tsp_ortools(self.list_points, distance="euclidean")

            self.assertIsInstance(result, RouteResult)
            self.assertEqual(len(result.route), len(self.list_points) + 1)  # +1 for return

        except ImportError:
            self.skipTest("OR-Tools not available")

    def test_high_level_shortest_path_function(self):
        """Test the high-level shortest_path function."""
        try:
            result = shortest_path(self.test_points, method="ortools", distance="euclidean")

            self.assertIsInstance(result, RouteResult)
            self.assertEqual(result.metadata["method"], "ortools")

        except ImportError:
            self.skipTest("OR-Tools not available")

    def test_christofides_solves_a_tour(self):
        """Christofides returns a tour that visits every point exactly once.

        This replaces ``test_christofides_import_error_handling``, which asserted
        that ``tsp_christofides`` *raises* ImportError. That only happens when the
        ``algorithms`` extra is absent, so the test meant one thing in the plain
        test job and the opposite in test-algorithms -- and it passed only
        because nobody had installed the extra on that runner.

        Running it the other way is what showed the function had never worked on
        Python 3: the Christofides package on PyPI is Python 2 source and raises
        SyntaxError on import. It now uses networkx's approximation, which is a
        hard dependency already, so there is no optional import left to test.
        """
        result = tsp_christofides(self.test_points)
        n_points = len(self.test_points)

        self.assertIsInstance(result, RouteResult)
        # Closed tour, matching tsp_ortools: every point once, then back to the
        # start. The two solvers are interchangeable through shortest_path(), so
        # they must agree on what a route is.
        self.assertEqual(len(result.route), n_points + 1)
        self.assertEqual(result.route[0], result.route[-1])
        self.assertEqual(sorted(result.route[:-1]), list(range(n_points)))
        self.assertGreater(result.total_distance, 0)

    def test_christofides_stays_within_its_approximation_guarantee(self):
        """The property that makes Christofides worth using over any other tour.

        It is a 3/2-approximation on a metric instance, so on a problem small
        enough to solve exactly the tour must be no worse than 1.5x optimal. A
        merely "valid" tour -- every point once, positive length -- would also be
        produced by visiting the points in input order, so without this the test
        above does not distinguish the algorithm from doing nothing.
        """
        result = tsp_christofides(self.test_points)

        # Score the tour in the metric the solver actually optimised in.
        # `euclidean` projects lon/lat to UTM metres before measuring
        # (allocator/distances/euclidean.py, utm.from_latlon), so scoring with
        # distances computed from raw degrees would compare a UTM-optimal tour
        # against a degree-optimal one. That is a different problem, and its
        # ratio can exceed 3/2 through projection distortion alone.
        points = self.test_points[["longitude", "latitude"]].to_numpy()
        n = len(points)
        distances = get_distance_matrix(points, points, method="euclidean")

        optimal = min(
            sum(distances[order[i], order[i + 1]] for i in range(n - 1))
            + distances[order[-1], order[0]]
            for order in itertools.permutations(range(n))
        )
        # result.route is the closed tour; drop the repeated start to iterate.
        route = result.route[:-1]
        tour = (
            sum(distances[route[i], route[i + 1]] for i in range(n - 1))
            + distances[route[-1], route[0]]
        )

        self.assertLessEqual(
            tour,
            1.5 * optimal,
            f"tour {tour:.4f} exceeds 1.5x the optimum {optimal:.4f}",
        )

    def test_invalid_method(self):
        """Test error handling for invalid TSP method."""
        with self.assertRaises(ValueError) as cm:
            shortest_path(self.test_points, method="invalid_method")

        self.assertIn("Unknown routing method", str(cm.exception))

    def test_empty_data(self):
        """Test error handling for empty data."""
        empty_data = pd.DataFrame(columns=["longitude", "latitude"])

        with self.assertRaises((ValueError, IndexError)):
            tsp_ortools(empty_data)

    def test_single_point(self):
        """Test TSP with single point."""
        single_point = pd.DataFrame({"longitude": [101.0], "latitude": [13.0]})

        try:
            result = tsp_ortools(single_point, distance="euclidean")
            # Should return a route that starts and ends at the same point
            self.assertEqual(len(set(result.route)), 1)

        except (ImportError, ValueError, IndexError):
            # Acceptable to fail with insufficient data or missing OR-Tools
            pass

    def test_route_metadata(self):
        """Test that route metadata is properly populated."""
        try:
            result = tsp_ortools(self.test_points, distance="haversine")

            expected_keys = ["method", "distance", "n_points"]
            for key in expected_keys:
                self.assertIn(key, result.metadata)

            self.assertEqual(result.metadata["method"], "ortools")
            self.assertEqual(result.metadata["distance"], "haversine")
            self.assertEqual(result.metadata["n_points"], len(self.test_points))

        except ImportError:
            self.skipTest("OR-Tools not available")

    def test_route_order_consistency(self):
        """Test that route order in data matches route list."""
        try:
            result = tsp_ortools(self.test_points, distance="euclidean")

            # Check that route_order column matches the route indices
            route_orders = result.data["route_order"].tolist()
            expected_orders = list(range(len(result.route)))
            self.assertEqual(route_orders, expected_orders)

        except ImportError:
            self.skipTest("OR-Tools not available")

    def test_different_distance_metrics(self):
        """Test TSP with different distance metrics."""
        distance_metrics = ["euclidean", "haversine"]

        for distance in distance_metrics:
            with self.subTest(distance=distance):
                try:
                    result = tsp_ortools(self.test_points, distance=distance)
                    self.assertGreater(result.total_distance, 0)
                    self.assertEqual(result.metadata["distance"], distance)

                except ImportError:
                    self.skipTest(f"OR-Tools not available for {distance}")


if __name__ == "__main__":
    unittest.main()
