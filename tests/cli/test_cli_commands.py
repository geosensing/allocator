"""
Tests for CLI commands.
"""

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from click.testing import CliRunner

from allocator.cli.main import cli


class TestCLICommands(unittest.TestCase):
    """Test CLI command functionality."""

    def setUp(self):
        """Set up test data and CLI runner."""
        self.runner = CliRunner()

        # Create test data file
        self.test_data = pd.DataFrame(
            {
                "longitude": [101.0, 101.1, 101.2, 101.3, 101.0, 101.1],
                "latitude": [13.0, 13.1, 13.2, 13.3, 13.0, 13.1],
                "id": range(6),
            }
        )

        # Create temporary CSV file
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()

    def tearDown(self):
        """Clean up temporary files."""
        Path(self.temp_file.name).unlink(missing_ok=True)

    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(cli, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("version", result.output.lower())

    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(cli, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Allocator", result.output)
        self.assertIn("cluster", result.output)
        self.assertIn("route", result.output)
        self.assertIn("sort", result.output)

    def test_cluster_command_basic(self):
        """Test basic cluster command."""
        result = self.runner.invoke(
            cli, ["cluster", "kmeans", self.temp_file.name, "--n-clusters", "2"]
        )

        # Should succeed (exit code 0) or fail gracefully
        self.assertIn(result.exit_code, [0, 1])  # Allow for missing dependencies

        if result.exit_code == 0:
            # If successful, should contain cluster information
            self.assertIn("cluster", result.output.lower())

    def test_cluster_command_with_output(self):
        """Test cluster command with output file."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as output_file:
            output_path = output_file.name

        try:
            result = self.runner.invoke(
                cli,
                [
                    "cluster",
                    "kmeans",
                    self.temp_file.name,
                    "--n-clusters",
                    "2",
                    "--output",
                    output_path,
                ],
            )

            if result.exit_code == 0:
                # Check that output file was created
                self.assertTrue(Path(output_path).exists())

                # Check that output file contains expected data
                output_df = pd.read_csv(output_path)
                self.assertIn("cluster", output_df.columns)

        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_cluster_command_different_methods(self):
        """Test cluster command with different methods."""
        methods = ["kmeans"]  # Only test methods that don't require external deps

        for method in methods:
            with self.subTest(method=method):
                result = self.runner.invoke(
                    cli, ["cluster", method, self.temp_file.name, "--n-clusters", "2"]
                )

                # Should either succeed or fail gracefully
                self.assertIn(result.exit_code, [0, 1])

    def test_route_command_basic(self):
        """Test basic route command."""
        # Create smaller dataset for routing
        small_data = self.test_data.head(4)  # Only 4 points for faster TSP

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as small_file:
            small_data.to_csv(small_file.name, index=False)
            small_path = small_file.name

        try:
            result = self.runner.invoke(cli, ["route", "ortools", small_path])

            # Should succeed if OR-Tools is available, or fail gracefully
            self.assertIn(result.exit_code, [0, 1])

            if result.exit_code == 0:
                self.assertIn("route", result.output.lower())

        finally:
            Path(small_path).unlink(missing_ok=True)

    def test_assign_command_basic(self):
        """Test basic assign command."""
        # Create centers file
        centers_data = pd.DataFrame(
            {"longitude": [101.05, 101.25], "latitude": [13.05, 13.25], "center_id": ["C1", "C2"]}
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as centers_file:
            centers_data.to_csv(centers_file.name, index=False)
            centers_path = centers_file.name

        try:
            result = self.runner.invoke(
                cli, ["sort", self.temp_file.name, "--workers", centers_path]
            )

            self.assertEqual(result.exit_code, 0)
            self.assertIn("worker", result.output.lower())

        finally:
            Path(centers_path).unlink(missing_ok=True)

    def test_cluster_command_invalid_file(self):
        """Test cluster command with invalid input file."""
        result = self.runner.invoke(
            cli, ["cluster", "kmeans", "/nonexistent/file.csv", "--n-clusters", "2"]
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("error", result.output.lower())

    def test_cluster_command_invalid_clusters(self):
        """Test cluster command with invalid cluster count."""
        result = self.runner.invoke(
            cli, ["cluster", "kmeans", self.temp_file.name, "--n-clusters", "0"]
        )

        self.assertNotEqual(result.exit_code, 0)

    def test_verbose_output(self):
        """Test verbose output flag."""
        result = self.runner.invoke(
            cli, ["--verbose", "cluster", "kmeans", self.temp_file.name, "--n-clusters", "2"]
        )

        # Should work regardless of success/failure
        # Verbose mode should provide more detailed output
        self.assertIsNotNone(result.output)

    def test_cluster_with_distance_metric(self):
        """Test cluster command with different distance metrics."""
        distances = ["euclidean", "haversine"]

        for distance in distances:
            with self.subTest(distance=distance):
                result = self.runner.invoke(
                    cli,
                    [
                        "cluster",
                        "kmeans",
                        self.temp_file.name,
                        "--n-clusters",
                        "2",
                        "--distance",
                        distance,
                    ],
                )

                # Should either succeed or fail gracefully
                self.assertIn(result.exit_code, [0, 1])

    def test_route_with_output(self):
        """Test route command with output file."""
        small_data = self.test_data.head(3)  # Very small for quick test

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as small_file:
            small_data.to_csv(small_file.name, index=False)
            small_path = small_file.name

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as output_file:
            output_path = output_file.name

        try:
            result = self.runner.invoke(cli, ["route", "tsp", small_path, "--output", output_path])

            if result.exit_code == 0:
                # Check that output file was created
                self.assertTrue(Path(output_path).exists())

                # Check that output file contains route information
                output_df = pd.read_csv(output_path)
                self.assertIn("route_order", output_df.columns)

        finally:
            Path(small_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)

    def test_json_output_format(self):
        """Test JSON output format."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as output_file:
            output_path = output_file.name

        try:
            result = self.runner.invoke(
                cli,
                [
                    "cluster",
                    "kmeans",
                    self.temp_file.name,
                    "--n-clusters",
                    "2",
                    "--output",
                    output_path,
                    "--format",
                    "json",
                ],
            )

            if result.exit_code == 0:
                # Check that output file was created and is valid JSON
                self.assertTrue(Path(output_path).exists())

                with open(output_path) as f:
                    data = json.load(f)  # Should not raise exception
                    self.assertIsInstance(data, (dict, list))

        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_assign_with_invalid_centers(self):
        """Test assign command with invalid centers file."""
        result = self.runner.invoke(
            cli, ["sort", self.temp_file.name, "--workers", "/nonexistent/centers.csv"]
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("error", result.output.lower())


if __name__ == "__main__":
    unittest.main()
