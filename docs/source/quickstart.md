# Quick Start Tutorial

Get up and running with allocator in minutes! This tutorial shows you the core functionality with practical examples.

## 1. Installation

First, install allocator:

```bash
pip install allocator
```

For the complete feature set:

```bash
pip install "allocator[all]"
```

See the [Installation Guide](installation.md) for detailed instructions and optional dependencies.

## 2. Basic Usage

### Import and Sample Data

```python
import pandas as pd
import allocator

# Create sample delivery locations in Bangkok
locations = pd.DataFrame({
    'longitude': [100.5018, 100.5065, 100.5108, 100.5157, 100.5201, 100.5243],
    'latitude': [13.7563, 13.7590, 13.7633, 13.7645, 13.7678, 13.7695],
    'location_id': ['Store_A', 'Store_B', 'Store_C', 'Store_D', 'Store_E', 'Store_F']
})

print(f"Sample dataset: {len(locations)} locations")
print(locations.head())
```

### Clustering: Group Geographic Points

```python
# Group locations into delivery zones
clusters = allocator.cluster(
    data=locations,
    n_clusters=3,
    distance='haversine'  # Geographic distance
)

print(f"✓ Created {clusters['n_clusters']} delivery zones")
print(f"Cluster assignments:\n{clusters['data'][['location_id', 'cluster']]}")

# Cluster statistics
for i in range(clusters['n_clusters']):
    cluster_data = clusters['data'][clusters['data']['cluster'] == i]
    print(f"Zone {i}: {len(cluster_data)} locations")
```

### Routing: Find Optimal Paths

```python
# Find optimal delivery route through all locations
route = allocator.shortest_path(
    data=locations,
    method='ortools'  # High-performance solver
)

print(f"✓ Optimal route: {route['total_distance']:.1f}km")
print(f"Route order:")
for i, location in enumerate(route['data']['location_id']):
    print(f"  {i+1}. {location}")
```

### Assignment: Connect to Service Centers

```python
# Define distribution centers
centers = pd.DataFrame({
    'longitude': [100.5000, 100.5150, 100.5300],
    'latitude': [13.7500, 13.7600, 13.7700],
    'center_id': ['North_DC', 'Central_DC', 'South_DC']
})

# Assign each location to closest center
assignments = allocator.assign(
    points=locations,
    workers=centers
)

print(f"✓ Assigned {len(assignments)} locations to distribution centers")

# Assignment summary
for center in centers['center_id']:
    assigned = assignments[assignments['worker_id'] == center]
    avg_distance = assigned['distance'].mean()
    print(f"{center}: {len(assigned)} locations, avg {avg_distance:.2f}km")
```

## 3. Command Line Interface

Allocator also provides a powerful CLI for batch processing:

```bash
# Create a CSV file with your data
echo "longitude,latitude,location_id
100.5018,13.7563,Store_A
100.5065,13.7590,Store_B
100.5108,13.7633,Store_C" > my_locations.csv

# Run clustering
allocator cluster kmeans my_locations.csv --n-clusters 2 --output zones.csv

# Run routing  
allocator route ortools my_locations.csv --output route.csv

# View help for all commands
allocator --help
```

## 4. Real-World Examples

For comprehensive examples using real OpenStreetMap data from Delhi and Chonburi:

### Quick Demo (1-2 seconds)
```bash
uv run python examples/scripts/quick_start.py
```

### Performance Analysis (5-10 seconds)
```bash
uv run python examples/scripts/real_world_workflow.py
```

### Generate Visualizations (30-60 seconds)
```bash
uv run python examples/scripts/algorithm_comparison.py
```

See the [Examples Overview](examples/overview.md) for detailed documentation of all available workflows.

## 5. Data Requirements

Allocator requires data with specific column names:

### Required Columns
- `longitude` - Longitude coordinates (decimal degrees)
- `latitude` - Latitude coordinates (decimal degrees)

### Optional Columns  
- `location_id` - Unique identifier for each location
- Any other columns are preserved in results

### Example Data Format
```csv
longitude,latitude,location_id,address
100.5018,13.7563,Store_A,"123 Sukhumvit Road"
100.5065,13.7590,Store_B,"456 Silom Road"
100.5108,13.7633,Store_C,"789 Sathorn Road"
```

## 6. Key Features

### Distance Calculation Methods
- **euclidean**: Straight-line distance (fast, approximate)
- **haversine**: Great-circle distance (accurate for geographic coordinates)
- **osrm**: Driving distance via OSRM API (realistic but slower)
- **googlemaps**: Driving distance via Google Maps API (requires API key)

### Clustering Algorithms
- **kmeans**: K-means clustering (fast, balanced clusters)
- **custom**: Custom algorithms via sklearn integration

### Routing Methods
- **ortools**: Google OR-Tools (optimal solutions, fastest)
- **nearest**: Nearest neighbor heuristic (fast approximate)
- **christofides**: Christofides algorithm (optimal, requires optional dependency)

## 7. Performance Tips

- **Small datasets (≤50 points)**: All methods work well, sub-second execution
- **Medium datasets (50-200 points)**: Use haversine distance, OR-Tools routing
- **Large datasets (200+ points)**: Consider sampling or euclidean approximation
- **API rate limits**: Use local methods (euclidean/haversine) for development

## 8. Next Steps

- **API Reference**: [Detailed API Documentation](api/clustering.md)
- **Examples**: [Complete Example Gallery](examples/overview.md)
- **CLI Guide**: [Command Line Interface](cli.md)
- **Migration**: [Upgrading from v0.x](migration.md)

## 9. Getting Help

- **Documentation**: [Full Documentation](https://geosensing.github.io/allocator/)
- **Examples**: Run the examples in `examples/scripts/` directory
- **Issues**: [GitHub Issues](https://github.com/geosensing/allocator/issues)
- **Source Code**: [GitHub Repository](https://github.com/geosensing/allocator)

Ready to dive deeper? Check out the [Examples Overview](examples/overview.md) for comprehensive real-world workflows!