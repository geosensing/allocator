"""
Tests for the data handler module.
"""

import unittest
import tempfile
import json
from pathlib import Path
import numpy as np
import pandas as pd

from allocator.io.data_handler import DataHandler


class TestDataHandler(unittest.TestCase):
    """Test data handler functionality."""

    def setUp(self):
        """Set up test data."""
        self.test_data_modern = pd.DataFrame(
            {"longitude": [101.0, 101.1, 101.2], "latitude": [13.0, 13.1, 13.2], "id": [1, 2, 3]}
        )

        self.numpy_data = np.array([[101.0, 13.0], [101.1, 13.1], [101.2, 13.2]])

        self.list_data = [[101.0, 13.0], [101.1, 13.1], [101.2, 13.2]]

    def test_load_dataframe_modern_columns(self):
        """Test loading DataFrame with modern column names."""
        result = DataHandler.load_data(self.test_data_modern)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("longitude", result.columns)
        self.assertIn("latitude", result.columns)
        pd.testing.assert_frame_equal(result, self.test_data_modern)

    def test_load_numpy_array(self):
        """Test loading numpy array."""
        result = DataHandler.load_data(self.numpy_data)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("longitude", result.columns)
        self.assertIn("latitude", result.columns)
        self.assertEqual(len(result), 3)

        np.testing.assert_array_equal(result["longitude"].values, self.numpy_data[:, 0])
        np.testing.assert_array_equal(result["latitude"].values, self.numpy_data[:, 1])

    def test_load_list(self):
        """Test loading list of coordinates."""
        result = DataHandler.load_data(self.list_data)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("longitude", result.columns)
        self.assertIn("latitude", result.columns)
        self.assertEqual(len(result), 3)

        for i, (lon, lat) in enumerate(self.list_data):
            self.assertEqual(result.iloc[i]["longitude"], lon)
            self.assertEqual(result.iloc[i]["latitude"], lat)

    def test_load_csv_file(self):
        """Test loading CSV file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            self.test_data_modern.to_csv(f.name, index=False)
            csv_path = f.name

        try:
            result = DataHandler.load_data(csv_path)

            self.assertIsInstance(result, pd.DataFrame)
            self.assertIn("longitude", result.columns)
            self.assertIn("latitude", result.columns)
            self.assertEqual(len(result), 3)
        finally:
            Path(csv_path).unlink()

    def test_load_json_file(self):
        """Test loading JSON file."""
        json_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [101.0, 13.0]},
                    "properties": {"id": 1},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [101.1, 13.1]},
                    "properties": {"id": 2},
                },
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(json_data, f)
            json_path = f.name

        try:
            result = DataHandler.load_data(json_path)

            self.assertIsInstance(result, pd.DataFrame)
            self.assertIn("longitude", result.columns)
            self.assertIn("latitude", result.columns)
            self.assertEqual(len(result), 2)
        finally:
            Path(json_path).unlink()

    def test_load_geojson_file(self):
        """Test loading GeoJSON file."""
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [101.0, 13.0]},
                    "properties": {"id": 1},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [101.1, 13.1]},
                    "properties": {"id": 2},
                },
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".geojson", delete=False) as f:
            json.dump(geojson_data, f)
            geojson_path = f.name

        try:
            result = DataHandler.load_data(geojson_path)

            self.assertIsInstance(result, pd.DataFrame)
            self.assertIn("longitude", result.columns)
            self.assertIn("latitude", result.columns)
            self.assertEqual(len(result), 2)
        finally:
            Path(geojson_path).unlink()

    def test_standard_columns_only(self):
        """Test that only standard longitude/latitude columns are accepted."""
        # Test that standard columns work
        test_df = pd.DataFrame(
            {"longitude": [101.0, 101.1], "latitude": [13.0, 13.1], "id": [1, 2]}
        )

        result = DataHandler.load_data(test_df)
        self.assertIn("longitude", result.columns)
        self.assertIn("latitude", result.columns)

        # Test that non-standard columns are rejected
        bad_df = pd.DataFrame({"long": [101.0, 101.1], "lat": [13.0, 13.1], "id": [1, 2]})

        with self.assertRaises(ValueError) as cm:
            DataHandler.load_data(bad_df)

        error_msg = str(cm.exception)
        self.assertIn("longitude", error_msg)
        self.assertIn("latitude", error_msg)

    def test_invalid_file_path(self):
        """Test error handling for invalid file path."""
        with self.assertRaises(FileNotFoundError):
            DataHandler.load_data("/nonexistent/path/file.csv")

    def test_invalid_data_type(self):
        """Test error handling for invalid data types."""
        with self.assertRaises((ValueError, TypeError, FileNotFoundError)):
            DataHandler.load_data("invalid string that's not a file path")

    def test_missing_coordinate_columns(self):
        """Test error handling for missing coordinate columns."""
        bad_df = pd.DataFrame({"name": ["A", "B", "C"], "value": [1, 2, 3]})

        with self.assertRaises(ValueError) as cm:
            DataHandler.load_data(bad_df)

        error_msg = str(cm.exception)
        self.assertIn("longitude", error_msg)
        self.assertIn("latitude", error_msg)

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame(columns=["longitude", "latitude"])

        result = DataHandler.load_data(empty_df)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 0)
        self.assertIn("longitude", result.columns)
        self.assertIn("latitude", result.columns)

    def test_numpy_array_wrong_shape(self):
        """Test error handling for numpy arrays with wrong shape."""
        # Wrong number of columns
        bad_array = np.array([[1], [2], [3]])

        with self.assertRaises(ValueError):
            DataHandler.load_data(bad_array)

        # Too many columns (should work and preserve additional columns)
        wide_array = np.array([[101.0, 13.0, 1], [101.1, 13.1, 2]])
        result = DataHandler.load_data(wide_array)

        self.assertEqual(result.shape[1], 3)  # Should have longitude, latitude, col_2
        self.assertIn("longitude", result.columns)
        self.assertIn("latitude", result.columns)
        self.assertIn("col_2", result.columns)

    def test_preserve_additional_columns(self):
        """Test that additional columns are preserved."""
        df_with_extra = pd.DataFrame(
            {
                "longitude": [101.0, 101.1],
                "latitude": [13.0, 13.1],
                "name": ["Point A", "Point B"],
                "value": [10, 20],
            }
        )

        result = DataHandler.load_data(df_with_extra)

        # Should preserve all original columns
        for col in df_with_extra.columns:
            self.assertIn(col, result.columns)

        pd.testing.assert_frame_equal(result, df_with_extra)

    def test_string_coordinates(self):
        """Test handling of string coordinate values."""
        df_with_strings = pd.DataFrame(
            {
                "longitude": ["101.0", "101.1", "101.2"],
                "latitude": ["13.0", "13.1", "13.2"],
                "id": [1, 2, 3],
            }
        )

        result = DataHandler.load_data(df_with_strings)

        # Should convert to numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(result["longitude"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(result["latitude"]))

        expected_lons = [101.0, 101.1, 101.2]
        expected_lats = [13.0, 13.1, 13.2]

        np.testing.assert_array_almost_equal(result["longitude"].values, expected_lons)
        np.testing.assert_array_almost_equal(result["latitude"].values, expected_lats)


if __name__ == "__main__":
    unittest.main()
