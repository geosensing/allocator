# allocator: Optimal Geographic Task Allocation

[![PyPI version](https://img.shields.io/pypi/v/allocator.svg)](https://pypi.python.org/pypi/allocator)
[![Downloads](https://pepy.tech/badge/allocator)](https://pepy.tech/project/allocator)
[![CI](https://github.com/geosensing/allocator/actions/workflows/ci.yml/badge.svg)](https://github.com/geosensing/allocator/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-github.io-blue)](https://geosensing.github.io/allocator/)

**Allocator** provides a modern, Pythonic API for geographic task allocation, clustering, and routing optimization.

## Key Features

- **🎯 Clustering**: Group geographic points into balanced zones
- **🛣️ Routing**: Find optimal paths through locations (TSP solving)  
- **📍 Assignment**: Connect points to closest workers/centers
- **🚀 Performance**: Optimized algorithms with NumPy and scikit-learn
- **📦 Modern API**: Clean Python interface + unified CLI

## Quick Start

```bash
pip install allocator
```

```python
import allocator
import pandas as pd

# Geographic locations
locations = pd.DataFrame({
    'longitude': [100.5018, 100.5065, 100.5108],
    'latitude': [13.7563, 13.7590, 13.7633]
})

# Group into zones
clusters = allocator.cluster(locations, n_clusters=2)

# Find optimal route
route = allocator.shortest_path(locations)

# Assign to service centers
centers = pd.DataFrame({
    'longitude': [100.50, 100.52],
    'latitude': [13.75, 13.77]
})
assignments = allocator.assign(locations, centers)
```

## Documentation & Examples

- **📖 [Full Documentation](https://geosensing.github.io/allocator/)**
- **🚀 [Installation & Tutorial](https://geosensing.github.io/allocator/quickstart.html)**  
- **🔧 [API Reference](https://geosensing.github.io/allocator/api/clustering.html)**
- **💡 [Real-World Examples](https://geosensing.github.io/allocator/examples/overview.html)**

## License & Contributing

MIT License. Contributions welcome - see [Contributing Guide](https://geosensing.github.io/allocator/contributing.html).
