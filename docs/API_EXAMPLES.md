# Allocator v1.0 API Examples

This document provides comprehensive examples of the Allocator v1.0 API.

## Installation

```bash
pip install allocator

# Optional dependencies for additional algorithms
pip install ortools  # For OR-Tools TSP solver
pip install googlemaps  # For Google Maps API
```

## Basic Usage

### Data Format

All functions require data with `longitude` and `latitude` columns:

```python
import pandas as pd
import allocator

# Required columns: longitude, latitude
data = pd.DataFrame({
    'longitude': [101.0, 101.1, 101.2, 101.3, 101.4],
    'latitude': [13.0, 13.1, 13.2, 13.3, 13.4],
    'location_id': ['A', 'B', 'C', 'D', 'E']
})

# You can also load from files
# data = pd.read_csv('locations.csv')
```

## Clustering

Group geographic points into balanced clusters for task allocation.

### K-means Clustering

```python
# Basic k-means clustering
result = allocator.kmeans(data, n_clusters=2, random_state=42)

print(f"Cluster labels: {result.labels}")
print(f"Centroids: {result.centroids}")
print(f"Converged: {result.converged}")
print(f"Iterations: {result.n_iter}")

# Access data with cluster assignments
clustered_data = result.data
print(clustered_data.head())
```

### High-level Clustering Interface

```python
# Use the high-level cluster function
result = allocator.cluster(
    data, 
    n_clusters=3, 
    method='kmeans',
    distance='haversine',
    random_state=42
)

# Results include rich metadata
print(result.metadata)
```

### Different Distance Metrics

```python
# Euclidean distance (fast, good for local areas)
result_euclidean = allocator.kmeans(data, n_clusters=2, distance='euclidean')

# Haversine distance (accounts for Earth's curvature)
result_haversine = allocator.kmeans(data, n_clusters=2, distance='haversine')

# Compare results
print(f"Euclidean inertia: {result_euclidean.inertia}")
print(f"Haversine inertia: {result_haversine.inertia}")
```

### KaHIP Graph Partitioning

```python
# KaHIP provides highly balanced clusters
# Requires: pip install kahipwrapper
try:
    result = allocator.kahip(data, n_clusters=3)
    print("KaHIP clustering successful!")
except ImportError:
    print("KaHIP not available - install kahipwrapper")
```

## Routing (TSP)

Find optimal paths through sets of locations.

### OR-Tools TSP Solver

```python
# OR-Tools provides exact solutions for small problems
route_result = allocator.tsp_ortools(data, distance='euclidean')

print(f"Optimal route: {route_result.route}")
print(f"Total distance: {route_result.total_distance}")
print(f"Route metadata: {route_result.metadata}")

# Access the ordered data
ordered_locations = route_result.data
print(ordered_locations[['location_id', 'route_order']])
```

### High-level Routing Interface

```python
# Use the high-level shortest_path function
route = allocator.shortest_path(
    data, 
    method='ortools',
    distance='haversine'
)

print(f"Route visits locations in order: {route.route}")
```

### Christofides Algorithm

```python
# Christofides provides 1.5-approximation
# Requires: pip install Christofides
try:
    route = allocator.tsp_christofides(data, distance='euclidean')
    print(f"Christofides route: {route.route}")
except ImportError:
    print("Christofides not available")
```

### OSRM Real-world Routing

```python
# Use real road networks via OSRM
# Note: Limited to ~25 points on public server
small_data = data.head(4)  # Use small dataset

try:
    route = allocator.shortest_path(small_data, method='osrm')
    print(f"OSRM road route: {route.route}")
    print(f"Total distance (meters): {route.total_distance}")
except Exception as e:
    print(f"OSRM error: {e}")
```

### Google Maps Routing

```python
# Use Google Maps Directions API
# Requires API key: export GOOGLE_MAPS_API_KEY=your_key
import os

if 'GOOGLE_MAPS_API_KEY' in os.environ:
    try:
        route = allocator.shortest_path(
            small_data, 
            method='google',
            api_key=os.environ['GOOGLE_MAPS_API_KEY']
        )
        print(f"Google Maps route: {route.route}")
    except Exception as e:
        print(f"Google Maps error: {e}")
```

## Assignment and Sorting

Assign points to workers or sort by distance.

### Assign to Closest Centers

```python
# Define worker/center locations
workers = pd.DataFrame({
    'longitude': [101.05, 101.25, 101.35],
    'latitude': [13.05, 13.25, 13.35],
    'worker_id': ['W1', 'W2', 'W3']
})

# Assign each point to closest worker
assignments = allocator.assign_to_closest(data, workers, distance='haversine')

print("Point assignments:")
print(assignments.data[['location_id', 'assigned_worker', 'worker_worker_id']])
```

### Sort by Distance

```python
# Sort all point-worker combinations by distance
sorted_assignments = allocator.sort_by_distance(
    data, 
    workers, 
    distance='euclidean'
)

print("All point-worker distances (sorted):")
print(sorted_assignments.data[['point_location_id', 'worker_worker_id', 'distance', 'rank']])
```

## Working with Files

### Loading Data from Files

```python
# Load from CSV
data = allocator.cluster('locations.csv', n_clusters=3)

# Load from different formats
# JSON/GeoJSON files are also supported
```

### Saving Results

```python
# Cluster and save results
result = allocator.cluster(data, n_clusters=3, method='kmeans')

# Save the clustered data
result.data.to_csv('clustered_locations.csv', index=False)

# Save just the cluster assignments
pd.DataFrame({
    'location_id': result.data['location_id'],
    'cluster': result.labels
}).to_csv('cluster_assignments.csv', index=False)
```

## Advanced Examples

### Multi-step Workflow

```python
# Complete workflow: cluster first, then route within each cluster
data = pd.DataFrame({
    'longitude': [101.0, 101.1, 101.2, 101.3, 101.4, 101.5],
    'latitude': [13.0, 13.1, 13.2, 13.3, 13.4, 13.5],
    'location_id': ['A', 'B', 'C', 'D', 'E', 'F']
})

# Step 1: Cluster locations
cluster_result = allocator.cluster(data, n_clusters=2, method='kmeans')

# Step 2: Route within each cluster
routes = {}
for cluster_id in range(2):
    cluster_points = cluster_result.data[cluster_result.data['cluster'] == cluster_id]
    
    if len(cluster_points) > 1:
        route = allocator.shortest_path(cluster_points, method='ortools')
        routes[f'cluster_{cluster_id}'] = route
        print(f"Cluster {cluster_id} route: {route.route}")
        print(f"Total distance: {route.total_distance}")
```

### Comparative Analysis

```python
# Compare different clustering methods
methods = ['kmeans']  # Add 'kahip' if available

results = {}
for method in methods:
    try:
        result = allocator.cluster(data, n_clusters=3, method=method, random_state=42)
        results[method] = result
        print(f"{method}: {result.inertia if hasattr(result, 'inertia') else 'N/A'}")
    except ImportError:
        print(f"{method} not available")

# Compare different distance metrics
distances = ['euclidean', 'haversine']
for distance in distances:
    result = allocator.cluster(data, n_clusters=3, distance=distance, random_state=42)
    print(f"{distance}: inertia = {result.inertia}")
```

### Error Handling

```python
# Handle missing dependencies gracefully
def safe_cluster(data, method='kmeans', **kwargs):
    try:
        return allocator.cluster(data, method=method, **kwargs)
    except ImportError as e:
        print(f"Method {method} not available: {e}")
        # Fallback to k-means
        return allocator.cluster(data, method='kmeans', **kwargs)

# Handle data validation
def validate_data(data):
    required_cols = ['longitude', 'latitude']
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return True

# Use with validation
try:
    validate_data(data)
    result = safe_cluster(data, method='kahip', n_clusters=3)
except ValueError as e:
    print(f"Data validation error: {e}")
```

## Command Line Interface

### Basic CLI Usage

```bash
# Cluster locations
allocator cluster locations.csv --clusters 3 --method kmeans --output clusters.csv

# Find optimal route
allocator route points.csv --method ortools --output route.csv

# Assign points to workers
allocator assign points.csv workers.csv --output assignments.csv
```

### Advanced CLI Options

```bash
# Use different distance metrics
allocator cluster data.csv --clusters 5 --distance haversine --output clusters.csv

# Specify output format
allocator route points.csv --method ortools --format json --output route.json

# Verbose output
allocator --verbose cluster data.csv --clusters 3
```

For more examples and complete API documentation, visit: https://geosensing.github.io/allocator/