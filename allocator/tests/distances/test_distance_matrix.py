"""
Tests for distance matrix calculations.
"""
import unittest
import numpy as np

from allocator.distances.distance_matrix import get_distance_matrix


class TestDistanceMatrix(unittest.TestCase):
    """Test distance matrix calculation functions."""
    
    def setUp(self):
        """Set up test data."""
        # Simple test points
        self.points_a = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0]
        ])
        
        self.points_b = np.array([
            [0.5, 0.5],
            [1.5, 1.5]
        ])
        
        # Geographic coordinates for testing haversine
        self.geo_points = np.array([
            [101.0, 13.0],  # Bangkok area
            [101.1, 13.1],
            [101.2, 13.2]
        ])
    
    def test_euclidean_distance_same_points(self):
        """Test euclidean distance matrix for same set of points."""
        distances = get_distance_matrix(self.points_a, method='euclidean')
        
        self.assertEqual(distances.shape, (3, 3))
        
        # Diagonal should be zero
        np.testing.assert_array_almost_equal(np.diag(distances), [0, 0, 0])
        
        # Matrix should be symmetric
        np.testing.assert_array_almost_equal(distances, distances.T)
        
        # Check specific distances
        # Distance from (0,0) to (1,0) should be 1.0
        self.assertAlmostEqual(distances[0, 1], 1.0, places=6)
        
        # Distance from (0,0) to (0,1) should be 1.0
        self.assertAlmostEqual(distances[0, 2], 1.0, places=6)
        
        # Distance from (1,0) to (0,1) should be sqrt(2)
        self.assertAlmostEqual(distances[1, 2], np.sqrt(2), places=6)
    
    def test_euclidean_distance_different_points(self):
        """Test euclidean distance matrix between different point sets."""
        distances = get_distance_matrix(self.points_a, self.points_b, method='euclidean')
        
        self.assertEqual(distances.shape, (3, 2))
        
        # Distance from (0,0) to (0.5,0.5) should be sqrt(0.5)
        expected_dist = np.sqrt(0.5**2 + 0.5**2)
        self.assertAlmostEqual(distances[0, 0], expected_dist, places=6)
    
    def test_haversine_distance(self):
        """Test haversine distance calculation."""
        distances = get_distance_matrix(self.geo_points, method='haversine')
        
        self.assertEqual(distances.shape, (3, 3))
        
        # Diagonal should be zero
        np.testing.assert_array_almost_equal(np.diag(distances), [0, 0, 0])
        
        # Matrix should be symmetric
        np.testing.assert_array_almost_equal(distances, distances.T)
        
        # All distances should be positive (except diagonal)
        self.assertTrue(np.all(distances >= 0))
        
        # Distances should be reasonable for geographic coordinates
        # (roughly in kilometers for these coordinates)
        self.assertTrue(np.all(distances[distances > 0] > 1000))  # At least 1km
        self.assertTrue(np.all(distances < 100000))  # Less than 100km
    
    def test_invalid_distance_method(self):
        """Test error handling for invalid distance method."""
        with self.assertRaises(ValueError) as cm:
            get_distance_matrix(self.points_a, method='invalid_method')
        
        self.assertIn('Unknown distance method', str(cm.exception))
    
    def test_empty_points(self):
        """Test behavior with empty point arrays."""
        empty_points = np.array([]).reshape(0, 2)
        
        distances = get_distance_matrix(empty_points, method='euclidean')
        
        self.assertEqual(distances.shape, (0, 0))
    
    def test_single_point(self):
        """Test distance matrix with single point."""
        single_point = np.array([[0.0, 0.0]])
        
        distances = get_distance_matrix(single_point, method='euclidean')
        
        self.assertEqual(distances.shape, (1, 1))
        self.assertEqual(distances[0, 0], 0.0)
    
    def test_different_shapes_error(self):
        """Test error handling for points with wrong dimensions."""
        # Points should be 2D coordinates
        wrong_shape = np.array([[1, 2, 3], [4, 5, 6]])  # 3D coordinates
        
        # Should handle gracefully or raise appropriate error
        try:
            distances = get_distance_matrix(wrong_shape, method='euclidean')
            # If it doesn't raise an error, it should at least work with first 2 dimensions
            self.assertIsNotNone(distances)
        except (ValueError, IndexError):
            # This is also acceptable behavior
            pass
    
    def test_none_points_to(self):
        """Test behavior when points_to is None (should use points_from)."""
        distances = get_distance_matrix(self.points_a, None, method='euclidean')
        
        # Should be same as get_distance_matrix(self.points_a, self.points_a)
        expected = get_distance_matrix(self.points_a, self.points_a, method='euclidean')
        
        np.testing.assert_array_almost_equal(distances, expected)
    
    def test_distance_matrix_properties(self):
        """Test mathematical properties of distance matrices."""
        distances = get_distance_matrix(self.points_a, method='euclidean')
        
        # Triangle inequality: d(a,c) <= d(a,b) + d(b,c)
        for i in range(len(self.points_a)):
            for j in range(len(self.points_a)):
                for k in range(len(self.points_a)):
                    triangle_sum = distances[i, j] + distances[j, k]
                    self.assertLessEqual(distances[i, k], triangle_sum + 1e-10)  # Small tolerance for floating point
    
    def test_haversine_vs_euclidean(self):
        """Test that haversine and euclidean give different results for geographic data."""
        euclidean_dist = get_distance_matrix(self.geo_points, method='euclidean')
        haversine_dist = get_distance_matrix(self.geo_points, method='haversine')
        
        # Should be different (haversine accounts for Earth's curvature)
        self.assertFalse(np.allclose(euclidean_dist, haversine_dist))
        
        # Haversine distances should generally be larger for geographic coordinates
        # (except for very small distances where the difference is negligible)
        non_zero_mask = euclidean_dist > 1e-6
        if np.any(non_zero_mask):
            # At least some haversine distances should be larger
            self.assertTrue(np.any(haversine_dist[non_zero_mask] > euclidean_dist[non_zero_mask]))
    
    def test_distance_matrix_symmetry(self):
        """Test that distance matrices are symmetric for same point sets."""
        for method in ['euclidean', 'haversine']:
            with self.subTest(method=method):
                distances = get_distance_matrix(self.points_a, method=method)
                
                # Should be symmetric
                np.testing.assert_array_almost_equal(distances, distances.T)
    
    def test_distance_matrix_zero_diagonal(self):
        """Test that diagonal elements are zero for same point sets."""
        for method in ['euclidean', 'haversine']:
            with self.subTest(method=method):
                distances = get_distance_matrix(self.points_a, method=method)
                
                # Diagonal should be zero
                diagonal = np.diag(distances)
                np.testing.assert_array_almost_equal(diagonal, np.zeros_like(diagonal))
    
    def test_consistent_results(self):
        """Test that multiple calls give consistent results."""
        dist1 = get_distance_matrix(self.points_a, method='euclidean')
        dist2 = get_distance_matrix(self.points_a, method='euclidean')
        
        np.testing.assert_array_equal(dist1, dist2)


if __name__ == '__main__':
    unittest.main()