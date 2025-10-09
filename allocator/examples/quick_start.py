#!/usr/bin/env python3
"""
Quick start example for allocator v1.0
"""

import allocator
import pandas as pd

# Create sample data
print("📍 Creating sample geographic data...")
data = pd.DataFrame(
    {
        "longitude": [101.0, 101.1, 101.2, 101.3, 101.0, 101.1],
        "latitude": [13.0, 13.1, 13.2, 13.3, 13.0, 13.1],
        "location_id": ["A", "B", "C", "D", "E", "F"],
    }
)
print(f"Data: {len(data)} locations around Bangkok area")
print(data)

print("\n🎯 1. Clustering locations...")
# Cluster locations into groups
cluster_result = allocator.cluster(data, n_clusters=2, method="kmeans")
print(f"✓ Clustered into {cluster_result.metadata['n_clusters']} groups")
print("Cluster assignments:")
print(cluster_result.data[["location_id", "longitude", "latitude", "cluster"]])

print("\n🛣️ 2. Finding optimal route...")
# Find optimal route through first 4 locations (smaller for demo)
route_data = data.head(4)
route_result = allocator.shortest_path(route_data, method="ortools")
print(f"✓ Route found with total distance: {route_result.total_distance:.1f}m")
print(f"Route order: {route_result.route}")
print("Route details:")
print(route_result.data[["location_id", "longitude", "latitude", "route_order"]])

print("\n📍 3. Assigning to closest workers...")
# Define worker locations
workers = pd.DataFrame(
    {
        "longitude": [101.05, 101.25],
        "latitude": [13.05, 13.25],
        "worker_id": ["Worker_1", "Worker_2"],
    }
)

assignment_result = allocator.assign_to_closest(data, workers)
print("✓ Assigned each location to closest worker")
print("Assignments:")
print(assignment_result.data[["location_id", "longitude", "latitude", "assigned_worker"]])

print("\n🎉 Demo complete! All functions working correctly.")
print(f"✓ Allocator v{allocator.__version__} ready for production use!")
