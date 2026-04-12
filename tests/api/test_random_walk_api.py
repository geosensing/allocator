"""
Tests for the random walk itinerary generation API.
"""

import unittest

import networkx as nx
import numpy as np

from allocator.api import random_walk
from allocator.api.types import RandomWalkResult
from allocator.core.random_walk import (
    _build_adjacency,
    _get_edge_length,
    _get_node_pos,
    generate_walk,
    generate_walks,
    validate_graph,
)


class TestRandomWalkAPI(unittest.TestCase):
    """Test random walk API functions."""

    def setUp(self):
        self.simple_graph = nx.Graph()
        self.simple_graph.add_node(0, longitude=100.0, latitude=13.0)
        self.simple_graph.add_node(1, longitude=100.1, latitude=13.0)
        self.simple_graph.add_node(2, longitude=100.1, latitude=13.1)
        self.simple_graph.add_edge(0, 1, length=1000.0)
        self.simple_graph.add_edge(1, 2, length=1500.0)

        self.line_graph = nx.Graph()
        self.line_graph.add_node(0, x=100.0, y=13.0)
        self.line_graph.add_node(1, x=100.1, y=13.0)
        self.line_graph.add_edge(0, 1, length=1000.0)

        self.complex_graph = nx.Graph()
        for i in range(5):
            self.complex_graph.add_node(i, lon=100.0 + i * 0.01, lat=13.0)
        for i in range(4):
            self.complex_graph.add_edge(i, i + 1, length=500.0)
        self.complex_graph.add_edge(0, 4, length=2000.0)

    def test_random_walk_basic(self):
        result = random_walk(self.simple_graph, n_walks=5, walk_length_m=500.0, seed=42)

        self.assertIsInstance(result, RandomWalkResult)
        self.assertEqual(len(result.walks), 5)
        self.assertIsNotNone(result.data)
        self.assertIn("walk_id", result.data.columns)
        self.assertIn("longitude", result.data.columns)
        self.assertIn("latitude", result.data.columns)
        self.assertIn("cumulative_distance_m", result.data.columns)

    def test_walk_length_respected(self):
        result = random_walk(self.simple_graph, n_walks=10, walk_length_m=500.0, seed=42)

        for walk in result.walks:
            self.assertLessEqual(walk["total_distance_m"], 500.0 + 1e-6)

    def test_metadata_populated(self):
        result = random_walk(self.simple_graph, n_walks=3, walk_length_m=1000.0, seed=123)

        expected_keys = [
            "n_walks",
            "walk_length_m",
            "total_network_length_m",
            "n_nodes",
            "n_edges",
            "seed",
            "avg_actual_distance_m",
        ]
        for key in expected_keys:
            self.assertIn(key, result.metadata)

        self.assertEqual(result.metadata["n_walks"], 3)
        self.assertEqual(result.metadata["walk_length_m"], 1000.0)
        self.assertEqual(result.metadata["seed"], 123)

    def test_reproducibility_with_seed(self):
        result1 = random_walk(self.simple_graph, n_walks=5, walk_length_m=800.0, seed=42)
        result2 = random_walk(self.simple_graph, n_walks=5, walk_length_m=800.0, seed=42)

        for w1, w2 in zip(result1.walks, result2.walks, strict=True):
            self.assertEqual(w1["total_distance_m"], w2["total_distance_m"])
            self.assertEqual(len(w1["waypoints"]), len(w2["waypoints"]))

    def test_different_seeds_different_results(self):
        result1 = random_walk(self.complex_graph, n_walks=10, walk_length_m=700.0, seed=1)
        result2 = random_walk(self.complex_graph, n_walks=10, walk_length_m=700.0, seed=2)

        walks1_waypoints = [len(w["waypoints"]) for w in result1.walks]
        walks2_waypoints = [len(w["waypoints"]) for w in result2.walks]
        self.assertNotEqual(walks1_waypoints, walks2_waypoints)

    def test_start_points_provided(self):
        result = random_walk(
            self.simple_graph,
            n_walks=3,
            walk_length_m=500.0,
            start_points=[0, 1],
            seed=42,
        )

        self.assertEqual(len(result.walks), 3)
        self.assertTrue(result.metadata["start_points_provided"])

    def test_x_y_coordinate_format(self):
        result = random_walk(self.line_graph, n_walks=2, walk_length_m=500.0, seed=42)

        self.assertIsInstance(result, RandomWalkResult)
        self.assertEqual(len(result.walks), 2)

    def test_dataframe_structure(self):
        result = random_walk(self.simple_graph, n_walks=3, walk_length_m=1000.0, seed=42)

        expected_columns = ["walk_id", "sequence", "longitude", "latitude", "cumulative_distance_m"]
        for col in expected_columns:
            self.assertIn(col, result.data.columns)

        walk_ids = result.data["walk_id"].unique()
        self.assertEqual(len(walk_ids), 3)

    def test_waypoints_have_increasing_distance(self):
        result = random_walk(self.simple_graph, n_walks=5, walk_length_m=2000.0, seed=42)

        for walk in result.walks:
            distances = [wp[2] for wp in walk["waypoints"]]
            for i in range(1, len(distances)):
                self.assertGreaterEqual(distances[i], distances[i - 1])

    def test_empty_graph_raises(self):
        empty_graph = nx.Graph()

        with self.assertRaises(ValueError):
            random_walk(empty_graph, n_walks=5, walk_length_m=1000.0)

    def test_graph_without_coords_raises(self):
        bad_graph = nx.Graph()
        bad_graph.add_node(0, name="A")
        bad_graph.add_node(1, name="B")
        bad_graph.add_edge(0, 1, length=100.0)

        with self.assertRaises(ValueError):
            random_walk(bad_graph, n_walks=5, walk_length_m=1000.0)

    def test_graph_without_lengths_raises(self):
        bad_graph = nx.Graph()
        bad_graph.add_node(0, longitude=100.0, latitude=13.0)
        bad_graph.add_node(1, longitude=100.1, latitude=13.0)
        bad_graph.add_edge(0, 1, name="edge1")

        with self.assertRaises(ValueError):
            random_walk(bad_graph, n_walks=5, walk_length_m=1000.0)


class TestCoreRandomWalkFunctions(unittest.TestCase):
    """Test core random walk functions."""

    def setUp(self):
        self.graph = nx.Graph()
        self.graph.add_node(0, longitude=100.0, latitude=13.0)
        self.graph.add_node(1, longitude=100.1, latitude=13.0)
        self.graph.add_node(2, longitude=100.1, latitude=13.1)
        self.graph.add_edge(0, 1, length=1000.0)
        self.graph.add_edge(1, 2, length=1500.0)

    def test_get_node_pos_longitude_latitude(self):
        lon, lat = _get_node_pos(self.graph, 0)
        self.assertEqual(lon, 100.0)
        self.assertEqual(lat, 13.0)

    def test_get_node_pos_x_y(self):
        g = nx.Graph()
        g.add_node(0, x=100.0, y=13.0)
        lon, lat = _get_node_pos(g, 0)
        self.assertEqual(lon, 100.0)
        self.assertEqual(lat, 13.0)

    def test_get_node_pos_lon_lat(self):
        g = nx.Graph()
        g.add_node(0, lon=100.0, lat=13.0)
        lon, lat = _get_node_pos(g, 0)
        self.assertEqual(lon, 100.0)
        self.assertEqual(lat, 13.0)

    def test_get_node_pos_missing_raises(self):
        g = nx.Graph()
        g.add_node(0, name="A")
        with self.assertRaises(ValueError):
            _get_node_pos(g, 0)

    def test_get_edge_length(self):
        length = _get_edge_length(self.graph, 0, 1)
        self.assertEqual(length, 1000.0)

    def test_get_edge_length_missing_raises(self):
        g = nx.Graph()
        g.add_node(0)
        g.add_node(1)
        g.add_edge(0, 1, name="test")
        with self.assertRaises(ValueError):
            _get_edge_length(g, 0, 1)

    def test_build_adjacency(self):
        adj = _build_adjacency(self.graph)

        self.assertIn(0, adj)
        self.assertIn(1, adj)
        self.assertIn(2, adj)

        self.assertEqual(len(adj[0]), 1)
        self.assertEqual(adj[0][0], (1, 1000.0))

        self.assertEqual(len(adj[1]), 2)

    def test_generate_walk(self):
        adj = _build_adjacency(self.graph)
        rng = np.random.default_rng(42)

        walk = generate_walk(self.graph, adj, 0, 500.0, rng)

        self.assertIn("waypoints", walk)
        self.assertIn("edges_traversed", walk)
        self.assertIn("total_distance_m", walk)
        self.assertLessEqual(walk["total_distance_m"], 500.0 + 1e-6)

    def test_generate_walk_partial_edge(self):
        adj = _build_adjacency(self.graph)
        rng = np.random.default_rng(42)

        walk = generate_walk(self.graph, adj, 0, 750.0, rng)

        self.assertLessEqual(walk["total_distance_m"], 750.0 + 1e-6)
        self.assertGreater(len(walk["waypoints"]), 1)

    def test_generate_walks_multiple(self):
        rng = np.random.default_rng(42)
        walks = generate_walks(self.graph, n_walks=5, walk_length_m=800.0, rng=rng)

        self.assertEqual(len(walks), 5)
        for walk in walks:
            self.assertIn("waypoints", walk)
            self.assertIn("total_distance_m", walk)

    def test_validate_graph_valid(self):
        result = validate_graph(self.graph)

        self.assertTrue(result["valid"])
        self.assertEqual(result["n_nodes"], 3)
        self.assertEqual(result["n_edges"], 2)
        self.assertEqual(result["nodes_with_coords"], 3)
        self.assertEqual(result["edges_with_length"], 2)
        self.assertEqual(result["total_network_length_m"], 2500.0)
        self.assertEqual(result["errors"], [])

    def test_validate_graph_invalid_no_coords(self):
        bad_graph = nx.Graph()
        bad_graph.add_node(0, name="A")
        bad_graph.add_edge(0, 0, length=100.0)

        result = validate_graph(bad_graph)

        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 0)

    def test_validate_graph_invalid_no_length(self):
        bad_graph = nx.Graph()
        bad_graph.add_node(0, longitude=100.0, latitude=13.0)
        bad_graph.add_node(1, longitude=100.1, latitude=13.0)
        bad_graph.add_edge(0, 1, name="edge")

        result = validate_graph(bad_graph)

        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 0)


class TestSelfWeightingProperty(unittest.TestCase):
    """Test that walks exhibit self-weighting behavior on simple networks."""

    def test_uniform_edge_traversal_over_many_walks(self):
        graph = nx.Graph()
        graph.add_node(0, longitude=100.0, latitude=13.0)
        graph.add_node(1, longitude=100.1, latitude=13.0)
        graph.add_node(2, longitude=100.0, latitude=13.1)
        graph.add_edge(0, 1, length=1000.0)
        graph.add_edge(1, 2, length=1000.0)
        graph.add_edge(2, 0, length=1000.0)

        result = random_walk(graph, n_walks=1000, walk_length_m=5000.0, seed=42)

        edge_traversals = {}
        for walk in result.walks:
            for u, v, _ in walk["edges_traversed"]:
                edge = tuple(sorted([u, v]))
                edge_traversals[edge] = edge_traversals.get(edge, 0) + 1

        if len(edge_traversals) > 1:
            counts = list(edge_traversals.values())
            mean_count = np.mean(counts)
            for count in counts:
                self.assertGreater(count, mean_count * 0.5)
                self.assertLess(count, mean_count * 1.5)


class TestDeadEndBehavior(unittest.TestCase):
    """Test behavior at dead ends."""

    def test_dead_end_reversal(self):
        graph = nx.Graph()
        graph.add_node(0, longitude=100.0, latitude=13.0)
        graph.add_node(1, longitude=100.1, latitude=13.0)
        graph.add_edge(0, 1, length=100.0)

        result = random_walk(graph, n_walks=10, walk_length_m=350.0, seed=42)

        for walk in result.walks:
            self.assertGreater(walk["total_distance_m"], 100.0)
            edges = walk["edges_traversed"]
            self.assertGreater(len(edges), 1)


if __name__ == "__main__":
    unittest.main()
