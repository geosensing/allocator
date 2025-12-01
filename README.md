# allocator: Optimally Allocate Geographically Distributed Tasks

[![PyPI version](https://img.shields.io/pypi/v/allocator.svg)](https://pypi.python.org/pypi/allocator)
[![Downloads](https://pepy.tech/badge/allocator)](https://pepy.tech/project/allocator)
[![CI](https://github.com/geosensing/allocator/actions/workflows/ci.yml/badge.svg)](https://github.com/geosensing/allocator/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-github.io-blue)](https://geosensing.github.io/allocator/)

**Allocator v1.0** provides a modern, Pythonic API for geographic task allocation, clustering, and routing optimization. 

How can we efficiently collect data from geographically distributed locations? Whether you're coordinating crowdsourced data collection, optimizing delivery routes, or planning field research, allocator provides the tools you need.

## ✨ What's New in v1.0

- **🎯 Modern Python API** - Clean, intuitive interface with type hints
- **📦 Unified CLI** - Single command with subcommands (`allocator cluster`, `allocator route`, `allocator assign`)
- **🚀 Performance** - Optimized algorithms with NumPy and scikit-learn
- **📊 Rich Results** - Structured results with metadata and easy export
- **🔧 No Backward Compatibility** - Clean slate, standards-compliant design

## Core Functionality

**1. Clustering** 🎯  
Group geographic points into balanced clusters for task allocation.

**2. Routing** 🛣️  
Find optimal paths through sets of locations (TSP solving).

**3. Assignment** 📍  
Assign points to closest workers/centers with distance-based sorting.

## Quick Start

### Installation

```bash
pip install allocator
```

### Python API Example

```python
import allocator
import pandas as pd

# Load your geographic data
data = pd.DataFrame({
    'longitude': [101.0, 101.1, 101.2, 101.3],
    'latitude': [13.0, 13.1, 13.2, 13.3],
    'location_id': ['A', 'B', 'C', 'D']
})

# Cluster locations into groups
result = allocator.cluster(data, n_clusters=2, method='kmeans')
print(f"Cluster labels: {result.labels}")
print(f"Centroids: {result.centroids}")

# Find optimal route through locations  
route = allocator.shortest_path(data, method='ortools')
print(f"Optimal route: {route.route}")
print(f"Total distance: {route.total_distance}")

# Assign points to closest centers
centers = pd.DataFrame({
    'longitude': [101.05, 101.25], 
    'latitude': [13.05, 13.25]
})
assignments = allocator.assign_to_closest(data, centers)
print(assignments.data)
```

### CLI Example

```bash
# Cluster geographic points
allocator cluster data.csv --clusters 3 --method kmeans --output clusters.csv

# Find optimal route  
allocator route locations.csv --method ortools --output route.csv

# Assign points to centers
allocator assign points.csv centers.csv --output assignments.csv
```

## Distance Metrics

All functions support multiple distance calculation methods:

- **euclidean** - Fast Euclidean distance (good for local areas)
- **haversine** - Great circle distance accounting for Earth's curvature  
- **osrm** - Real road network distances via OSRM API
- **google** - Google Maps distance matrix (requires API key)

## Algorithms

**Clustering:**
- **K-means**: Fast, well-balanced clusters
- **KaHIP**: Graph partitioning for highly balanced clusters (requires external install)

**Routing (TSP):**
- **OR-Tools**: Exact solutions for small problems, heuristics for larger ones
- **Christofides**: 1.5-approximation algorithm (requires external install)
- **OSRM**: Real-world routing via road networks
- **Google**: Google Maps Directions API

## Data Format

Input data must be pandas DataFrames or CSV files with these columns:

- **longitude**: Geographic longitude (required)
- **latitude**: Geographic latitude (required)  
- Additional columns are preserved in results

## Examples and Use Cases

- **Field Research**: Optimize survey routes for maximum efficiency
- **Delivery/Logistics**: Plan optimal delivery routes and territories  
- **Crowdsourcing**: Assign tasks to workers based on geographic proximity
- **Emergency Response**: Allocate resources to incident locations
- **Urban Planning**: Analyze spatial patterns and optimize service locations

## API Reference

### Main Functions

```python
# High-level functions
allocator.cluster(data, n_clusters=3, method='kmeans', distance='euclidean')
allocator.shortest_path(data, method='ortools', distance='euclidean') 
allocator.assign_to_closest(points, workers, distance='euclidean')

# Specific algorithms
allocator.kmeans(data, n_clusters=3, distance='euclidean')
allocator.kahip(data, n_clusters=3)  # Requires KaHIP installation
allocator.tsp_ortools(data, distance='euclidean')
allocator.tsp_christofides(data)  # Requires Christofides installation
```

### Result Types

- `ClusterResult`: Labels, centroids, convergence info, metadata
- `RouteResult`: Route order, total distance, metadata  
- `SortResult`: Sorted assignments with distances, metadata

## Requirements

- Python 3.11+
- Core: pandas, numpy, matplotlib, networkx, scikit-learn
- CLI: click, rich
- Optional: ortools, googlemaps, requests (for OSRM)

## Documentation

Complete documentation: https://geosensing.github.io/allocator/

## Development

This project uses modern Python development practices:

- **uv** for dependency management
- **pytest** for testing  
- **black** and **isort** for code formatting
- **ruff** for linting
- **GitHub Actions** for CI/CD

## Contributing

We welcome contributions! Please see our [Contributor Code of Conduct](http://contributor-covenant.org/version/1/0/0/).

## Authors

Suriyan Laohaprapanon and Gaurav Sood

## License

MIT License - see [LICENSE](https://opensource.org/licenses/MIT) for details.