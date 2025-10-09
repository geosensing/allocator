#!/usr/bin/env python3
"""
Example demonstrating different distance calculation methods.
"""

import allocator
import pandas as pd
import numpy as np

# Create sample data - Bangkok to nearby cities
print("🌏 Comparing distance calculation methods...")
cities = pd.DataFrame(
    {
        "longitude": [100.5018, 101.0, 101.5, 102.0],
        "latitude": [13.7563, 13.0, 14.0, 13.5],
        "city": ["Bangkok", "Close_City", "North_City", "East_City"],
    }
)

print("Cities:")
print(cities)

print("\n📏 1. Euclidean distance (straight line)...")
euclidean_result = allocator.cluster(cities, n_clusters=2, distance="euclidean")
print("Clusters with Euclidean distance:")
print(euclidean_result.data[["city", "cluster"]])

print("\n🌍 2. Haversine distance (great circle)...")
haversine_result = allocator.cluster(cities, n_clusters=2, distance="haversine")
print("Clusters with Haversine distance:")
print(haversine_result.data[["city", "cluster"]])

print("\n📊 3. Manual distance matrix calculation...")
points = cities[["longitude", "latitude"]].values

# Calculate different distance matrices
euclidean_matrix = allocator.euclidean_distance_matrix(points)
haversine_matrix = allocator.haversine_distance_matrix(points)

print(f"Euclidean distance Bangkok to Close_City: {euclidean_matrix[0, 1]:.1f}m")
print(f"Haversine distance Bangkok to Close_City: {haversine_matrix[0, 1]:.1f}m")

print("\n🔧 4. Using direct distance matrix function...")
distances = allocator.get_distance_matrix(points, method="haversine")
print("Distance matrix shape:", distances.shape)
print("All distances from Bangkok:")
for i, city in enumerate(cities["city"]):
    if i > 0:  # Skip Bangkok to itself
        print(f"  To {city}: {distances[0, i]:.1f}m")

print("\n✅ Different distance methods provide different clustering results!")
print("   • Euclidean: Fast but ignores Earth's curvature")
print("   • Haversine: Accurate for geographic distances")
print("   • OSRM: Real road distances (requires internet)")
print("   • Google: Most accurate with traffic (requires API key)")
