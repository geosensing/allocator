# Allocator: Modern Geographic Task Allocation

[![PyPI version](https://img.shields.io/pypi/v/allocator.svg)](https://pypi.python.org/pypi/allocator)
[![Downloads](https://pepy.tech/badge/allocator)](https://pepy.tech/project/allocator)
[![CI](https://github.com/geosensing/allocator/actions/workflows/ci.yml/badge.svg)](https://github.com/geosensing/allocator/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-github.io-blue)](https://geosensing.github.io/allocator/)

**Allocator v1.0** provides a modern, Pythonic API for geographic task allocation, clustering, and routing optimization.

How can we efficiently collect data from geographically distributed locations? Whether you're coordinating crowdsourced data collection, optimizing delivery routes, or planning field research, allocator provides the tools you need.

## What's New in v1.0

- **🎯 Modern Python API** - Clean, intuitive interface with type hints
- **📦 Unified CLI** - Single command with subcommands (`allocator cluster`, `allocator route`, `allocator assign`) 
- **🚀 Performance** - Optimized algorithms with NumPy and scikit-learn
- **📊 Rich Results** - Structured results with metadata and easy export
- **🔧 Clean Design** - No backward compatibility, standards-compliant from the ground up

## Core Functionality

### 1. Clustering 🎯
Group geographic points into balanced clusters for task allocation.

- **K-means clustering** with euclidean and haversine distances
- **Customizable cluster counts** and distance metrics
- **Geographic optimization** for real-world coordinates

### 2. Routing 🛣️
Find optimal paths through sets of locations (TSP solving).

- **OR-Tools integration** for high-performance route optimization
- **Multiple algorithms** including nearest neighbor and optimization solvers
- **Distance matrix support** with various calculation methods

### 3. Assignment 📍
Assign points to closest workers/centers with distance-based sorting.

- **Distance-based assignment** to minimize total travel
- **Capacity constraints** and load balancing
- **Multi-depot support** for complex scenarios

## Quick Start

```python
import pandas as pd
import allocator

# Sample data: delivery locations in Bangkok
locations = pd.DataFrame({
    'longitude': [100.5018, 100.5065, 100.5108, 100.5157],
    'latitude': [13.7563, 13.7590, 13.7633, 13.7645],
    'location_id': ['Store_A', 'Store_B', 'Store_C', 'Store_D']
})

# 1. Group into delivery zones
clusters = allocator.cluster(locations, n_clusters=2, distance='haversine')
print(f"Created {clusters['n_clusters']} delivery zones")

# 2. Find optimal delivery route
route = allocator.shortest_path(locations, method='ortools')
print(f"Optimal route covers {route['total_distance']:.1f}km")

# 3. Assign to closest distribution center  
centers = pd.DataFrame({
    'longitude': [100.5000, 100.5200],
    'latitude': [13.7500, 13.7700]
})
assignments = allocator.assign(locations, centers)
print(f"Assigned {len(assignments)} locations to distribution centers")
```

## Table of Contents

```{toctree}
:maxdepth: 2
:caption: Getting Started

installation
quickstart
migration
```

```{toctree}
:maxdepth: 2
:caption: API Reference

api/clustering
api/routing  
api/assignment
api/distances
```

```{toctree}
:maxdepth: 2
:caption: Examples & Workflows

examples/overview
examples/scripts
examples/data
```

```{toctree}
:maxdepth: 1
:caption: Development

contributing
changelog
```

## Business Applications

### Urban Planning 🏙️
- **Service Districts**: Police beats, school districts, utility service areas
- **Resource Allocation**: Emergency services, public transportation routes
- **Infrastructure Planning**: Optimal placement of facilities and services

### Logistics & Supply Chain 📦
- **Last-Mile Delivery**: Route optimization for package delivery
- **Field Service**: Technician scheduling and territory management
- **Inventory Management**: Warehouse allocation and distribution planning

### Research & Academia 📊
- **Data Collection**: Fieldwork planning and survey optimization
- **Spatial Analysis**: Geographic clustering and pattern recognition
- **Algorithm Development**: Benchmarking and method comparison

## Performance

Allocator v1.0 is built for production use with real-world datasets:

- **Small problems (≤50 points)**: Sub-second execution
- **Medium problems (50-200 points)**: 1-10 seconds
- **Large problems (200+ points)**: 10+ seconds with linear scaling

All algorithms are optimized using NumPy vectorization and scikit-learn implementations.

## Support & Community

- **Documentation**: Complete API reference and examples
- **Issues**: [GitHub Issues](https://github.com/geosensing/allocator/issues) for bug reports
- **Source Code**: [GitHub Repository](https://github.com/geosensing/allocator)
- **PyPI Package**: [allocator](https://pypi.org/project/allocator/)

## License

MIT License - see [LICENSE](https://github.com/geosensing/allocator/blob/main/LICENSE) for details.

---

**Ready to get started?** Check out the [Installation Guide](installation.md) and [Quick Start Tutorial](quickstart.md)!