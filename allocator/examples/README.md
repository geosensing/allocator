# Allocator v1.0 Examples

This directory contains example scripts demonstrating the key features of allocator v1.0.

## Quick Start Examples

### 1. **quick_start.py** - Basic API usage
```bash
python quick_start.py
```
Demonstrates the three main functions:
- Clustering geographic points
- Finding optimal routes (TSP)
- Assigning points to closest workers

### 2. **distance_methods.py** - Distance calculations
```bash
python distance_methods.py
```
Shows different distance calculation methods:
- Euclidean (straight line)
- Haversine (great circle)
- Manual distance matrices

### 3. **cli_examples.py** - Command-line interface
```bash
python cli_examples.py
```
Demonstrates the unified CLI commands:
- `allocator cluster kmeans`
- `allocator route ortools`
- `allocator sort`

## Running Examples

All examples use sample data around Bangkok, Thailand:

```bash
# From the allocator directory
cd allocator/examples
python quick_start.py
```

## Example Data Format

All examples expect data with these columns:
- `longitude` - Longitude coordinates (required)
- `latitude` - Latitude coordinates (required)
- Additional columns are preserved in results

```python
import pandas as pd

data = pd.DataFrame({
    'longitude': [101.0, 101.1, 101.2],
    'latitude': [13.0, 13.1, 13.2],
    'location_id': ['A', 'B', 'C']  # Optional
})
```

## Next Steps

For more comprehensive documentation:
- See [API_EXAMPLES.md](../docs/API_EXAMPLES.md) for detailed API usage
- Check [MIGRATION_GUIDE.md](../docs/MIGRATION_GUIDE.md) if upgrading from v0.x
- Visit the [online documentation](https://geosensing.github.io/allocator/)