# Installation Guide

## Requirements

**Python Version**: >=3.11  
**Operating System**: Windows, macOS, Linux

## Basic Installation

### Install from PyPI (Recommended)

```bash
pip install allocator
```

This installs the core allocator package with all essential dependencies for clustering, routing, and assignment operations.

### Install with UV (Fastest)

```bash
uv add allocator
```

UV is a modern, fast Python package manager. If you don't have UV installed:

```bash
pip install uv
uv add allocator
```

## Optional Dependencies

allocator supports several optional dependency groups for extended functionality:

### Algorithms

```bash
# Enhanced algorithms including Christofides TSP
pip install "allocator[algorithms]"
```

Includes:
- `scipy` ≥1.10.0 - Enhanced mathematical algorithms
- `Christofides` ≥1.0.0 - Christofides TSP algorithm for optimal routing

### Geo

```bash
# Interactive mapping and route visualization
pip install "allocator[geo]"
```

Includes:
- `folium` ≥0.14.0 - Interactive maps and visualizations
- `polyline` ≥2.0.0 - Route encoding for mapping APIs

### Dev

```bash
# Development and testing tools
pip install "allocator[dev]"
```

Includes:
- `ruff` ≥0.1.0 - Modern linting and formatting
- `mypy` ≥1.5.0 - Type checking
- `black` ≥23.0.0 - Code formatting
- `isort` ≥5.12.0 - Import sorting
- `pre-commit` ≥3.0.0 - Git hooks for code quality

### Test

```bash
# Testing framework and coverage tools
pip install "allocator[test]"
```

Includes:
- `pytest` ≥7.4.0 - Testing framework
- `pytest-cov` ≥4.1.0 - Coverage reporting
- `pytest-xdist` ≥3.3.0 - Parallel testing
- `coverage` ≥7.2.0 - Code coverage analysis
- `hypothesis` ≥6.82.0 - Property-based testing

### Docs

```bash
# Documentation building tools
pip install "allocator[docs]"
```

Includes:
- `sphinx` ≥7.0.0 - Documentation generator
- `furo` ≥2023.9.10 - Additional functionality
- `myst-parser` ≥2.0.0 - Markdown support for Sphinx
- `linkify-it-py` ≥2.0.0 - Additional functionality
- `sphinx-autodoc-typehints` ≥1.24.0 - Type hints in API docs
- `sphinx-design` ≥0.5.0 - Additional functionality

## Complete Installation

### All Features

```bash
# Install with all optional features
pip install "allocator[all]"
```

### Complete Development Setup

```bash
# Install everything for development
pip install "allocator[complete]"
```

## Installation Verification

### Quick Test

```python
import allocator
print(f"Allocator version: {allocator.__version__}")

# Test basic functionality
import pandas as pd

# Create sample data
data = pd.DataFrame({
    'longitude': [100.5, 100.6, 100.7],
    'latitude': [13.7, 13.8, 13.9]
})

# Test clustering
result = allocator.cluster(data, n_clusters=2)
print(f"✓ Clustering: Created {result['n_clusters']} clusters")

# Test routing  
route = allocator.shortest_path(data)
print(f"✓ Routing: {route['total_distance']:.1f}km route")

print("🎉 Installation successful!")
```

### Command Line Interface

```bash
# Test CLI installation
allocator --version

# Test clustering command
echo "longitude,latitude
100.5,13.7
100.6,13.8
100.7,13.9" > test_data.csv

allocator cluster kmeans test_data.csv --n-clusters 2
```

## Troubleshooting

### Common Issues

#### Permission Error on macOS/Linux

```bash
# Use --user flag to install in user directory
pip install --user allocator
```

#### Package Conflicts

```bash
# Create a virtual environment (recommended)
python -m venv allocator_env
source allocator_env/bin/activate  # On Windows: allocator_env\Scripts\activate
pip install allocator
```

#### UV Installation Issues

```bash
# Install UV using pip if direct install fails
pip install uv
uv add allocator
```

### Core Dependencies

allocator requires these core packages:

- **pandas ≥2.0.0** - Data manipulation and analysis
- **numpy ≥1.24.0** - Numerical computations
- **scikit-learn ≥1.3.0** - Machine learning algorithms
- **utm ≥0.7.0** - Coordinate system transformations
- **haversine ≥2.8.0** - Geographic distance calculations
- **networkx ≥3.0** - Graph algorithms
- **click ≥8.0.0** - Command-line interface framework
- **rich ≥13.0.0** - Rich terminal output and formatting
- **requests ≥2.28.0** - HTTP library for API calls
- **googlemaps ≥4.6.0** - Google Maps API integration
- **ortools ≥9.5.0** - High-performance optimization algorithms
- **matplotlib ≥3.6.0** - Basic plotting and visualization
- **seaborn ≥0.13.2** - Statistical data visualization

### System Requirements

**Memory**: 2GB+ recommended for large datasets (1000+ points)  
**Storage**: 100MB for package + 50MB per analysis run  
**Network**: Optional for OSRM/Google Maps API features

## Development Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/geosensing/allocator.git
cd allocator

# Install in development mode
pip install -e ".[complete]"

# Set up pre-commit hooks
pre-commit install
```

### Using UV

```bash
# Clone and install with UV
git clone https://github.com/geosensing/allocator.git
cd allocator
uv sync --all-extras
```

## Docker Installation

### Quick Start with Docker

```bash
# Run allocator in Docker container
docker run --rm -v $(pwd):/data python:3.11 bash -c "
    pip install allocator &&
    cd /data &&
    allocator --help
"
```

### Custom Dockerfile

```dockerfile
FROM python:3.11-slim

# Install allocator with all features
RUN pip install allocator[all]

# Set working directory
WORKDIR /workspace

# Default command
CMD ["allocator", "--help"]
```

Build and run:

```bash
docker build -t allocator .
docker run --rm -v $(pwd):/workspace allocator
```

## Local OSRM Server

For production workloads or offline use, run your own OSRM server instead of the public API.

### Setup

```bash
cd scripts/osrm

# Download and preprocess OSM data (default: California)
./setup.sh

# Or specify a different region (see https://download.geofabrik.de/)
./setup.sh europe/germany
./setup.sh asia/india
```

### Start Server

```bash
cd scripts/osrm
docker compose up -d
```

### Use with allocator

```python
from allocator.distances import get_distance_matrix

matrix = get_distance_matrix(
    points,
    method="osrm",
    osrm_base_url="http://localhost:5000"
)
```

### Stop Server

```bash
cd scripts/osrm
docker compose down
```

## Next Steps

- 📖 **Quick Start**: [Quickstart Tutorial](quickstart.md)
- 🔧 **API Reference**: [API Documentation](api/clustering.md)
- 💡 **Examples**: [Example Workflows](examples/overview.md)
- 🚀 **CLI Guide**: [Command Line Interface](cli.md)

## Getting Help

- **Documentation**: [https://geosensing.github.io/allocator/](https://geosensing.github.io/allocator/)
- **Issues**: [GitHub Issues](https://github.com/geosensing/allocator/issues)
- **Source**: [GitHub Repository](https://github.com/geosensing/allocator)
- **PyPI**: [Package Page](https://pypi.org/project/allocator/)