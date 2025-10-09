# Migration Guide: v0.x to v1.0

This guide helps you migrate from allocator v0.x to the completely redesigned v1.0.

## 🚨 Breaking Changes Overview

**Allocator v1.0 is a complete rewrite** with no backward compatibility. The changes provide:
- Modern Python API design
- Better performance and reliability  
- Cleaner, more maintainable codebase
- Rich structured results with metadata

## 📊 Data Format Changes

### Column Names (BREAKING)

**v0.x (Old):**
```python
# Accepted various column names
data = pd.DataFrame({
    'start_long': [101.0, 101.1],   # or 'lon', 'lng'
    'start_lat': [13.0, 13.1],      # or 'lat'
    'end_long': [101.2, 101.3],
    'end_lat': [13.2, 13.3]
})
```

**v1.0 (New):**
```python
# Only accepts standard column names
data = pd.DataFrame({
    'longitude': [101.0, 101.1],    # REQUIRED
    'latitude': [13.0, 13.1],       # REQUIRED
    'location_id': ['A', 'B']       # Optional, other columns preserved
})
```

**Migration:**
```python
# Rename columns in existing data
data = data.rename(columns={
    'start_long': 'longitude',
    'start_lat': 'latitude',
    'lon': 'longitude',
    'lat': 'latitude'
})
```

## 🔄 API Changes

### Clustering

**v0.x (Old):**
```python
from allocator.cluster_kmeans import main
result = main(data, n_clusters=3, distance_method='euclidean')
```

**v1.0 (New):**
```python
import allocator
result = allocator.cluster(data, n_clusters=3, method='kmeans', distance='euclidean')
# or
result = allocator.kmeans(data, n_clusters=3, distance='euclidean')
```

### Routing/TSP

**v0.x (Old):**
```python
from allocator.shortest_path_ortools import main
result = main(data, distance_method='euclidean')
```

**v1.0 (New):**
```python
import allocator
result = allocator.shortest_path(data, method='ortools', distance='euclidean')
# or  
result = allocator.tsp_ortools(data, distance='euclidean')
```

### Distance Assignment

**v0.x (Old):**
```python
from allocator.sort_by_distance import main
result = main(points, workers, by_worker=False)
```

**v1.0 (New):**
```python
import allocator
result = allocator.assign_to_closest(points, workers, distance='euclidean')
# or for sorting
result = allocator.sort_by_distance(points, workers, distance='euclidean')
```

## 🖥️ CLI Changes

### Command Structure

**v0.x (Old):**
```bash
# Separate scripts for each function
python -m allocator.cluster_kmeans data.csv -n 3 --plot
python -m allocator.shortest_path_ortools data.csv -d euclidean
python -m allocator.sort_by_distance points.csv workers.csv
```

**v1.0 (New):**
```bash
# Unified CLI with subcommands
allocator cluster data.csv --clusters 3 --method kmeans
allocator route data.csv --method ortools --distance euclidean  
allocator assign points.csv workers.csv --distance euclidean
```

### CLI Options Mapping

| v0.x | v1.0 | Description |
|------|------|-------------|
| `-n`, `--n_clusters` | `--clusters` | Number of clusters |
| `-d`, `--distance_method` | `--distance` | Distance metric |
| `--plot` | *(removed)* | Use Python API for plotting |
| `-o`, `--output` | `--output` | Output file path |
| *(none)* | `--format` | Output format (csv, json) |
| *(none)* | `--verbose` | Verbose output |

### CLI Examples

**Clustering:**
```bash
# Old
python -m allocator.cluster_kmeans locations.csv -n 5 -d haversine --plot

# New  
allocator cluster locations.csv --clusters 5 --distance haversine --output clusters.csv
```

**Routing:**
```bash
# Old
python -m allocator.shortest_path_ortools points.csv -d euclidean -o route.csv

# New
allocator route points.csv --method ortools --distance euclidean --output route.csv
```

**Assignment:**
```bash
# Old
python -m allocator.sort_by_distance points.csv workers.csv -o assignments.csv

# New  
allocator assign points.csv workers.csv --output assignments.csv
```

## 📦 Result Objects

### v0.x Return Values

**Old results were inconsistent:**
```python
# Different return types for different functions
kmeans_result = dict  # Dictionary with various keys
tsp_result = tuple    # (distance, route)  
sort_result = DataFrame  # Raw pandas DataFrame
```

### v1.0 Structured Results

**New consistent result objects:**
```python
# ClusterResult
cluster_result = allocator.cluster(data, n_clusters=3)
print(cluster_result.labels)        # np.ndarray
print(cluster_result.centroids)     # np.ndarray  
print(cluster_result.converged)     # bool
print(cluster_result.inertia)       # float
print(cluster_result.data)          # pd.DataFrame with cluster column
print(cluster_result.metadata)      # dict with algorithm info

# RouteResult  
route_result = allocator.shortest_path(data)
print(route_result.route)           # list[int] - visiting order
print(route_result.total_distance)  # float
print(route_result.data)            # pd.DataFrame with route_order column
print(route_result.metadata)        # dict with algorithm info

# SortResult
sort_result = allocator.assign_to_closest(points, workers)
print(sort_result.data)             # pd.DataFrame with assignments
print(sort_result.distance_matrix)  # np.ndarray (if available)
print(sort_result.metadata)         # dict with algorithm info
```

## 🔧 Installation Changes

### Dependencies

**v0.x:**
```bash
pip install allocator==0.2.x
# Dependencies automatically included
```

**v1.0:**
```bash
pip install allocator
# Core functionality included

# Optional algorithms:
pip install ortools          # For OR-Tools TSP
pip install googlemaps       # For Google Maps API  
pip install kahipwrapper     # For KaHIP clustering
```

### Python Version

- **v0.x**: Python 2.7+ / 3.6+
- **v1.0**: Python 3.11+ (modern Python required)

## 📈 Performance Improvements

**v1.0 provides significant performance improvements:**

- **3x faster** clustering with optimized algorithms
- **Reduced memory usage** for large datasets  
- **Vectorized operations** with NumPy/pandas
- **Better error handling** and progress reporting

## 🛠️ Step-by-Step Migration

### 1. Update Installation

```bash
# Uninstall old version
pip uninstall allocator

# Install new version  
pip install allocator

# Install optional dependencies as needed
pip install ortools  # For TSP solving
```

### 2. Update Data Preparation

```python
# Create a migration function
def migrate_data(old_data):
    """Convert v0.x data format to v1.0"""
    new_data = old_data.copy()
    
    # Rename columns
    column_mapping = {
        'start_long': 'longitude',
        'start_lat': 'latitude', 
        'end_long': 'longitude',
        'end_lat': 'latitude',
        'lon': 'longitude',
        'lng': 'longitude',
        'lat': 'latitude'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in new_data.columns:
            new_data = new_data.rename(columns={old_col: new_col})
    
    # Validate required columns
    required = ['longitude', 'latitude']
    missing = [col for col in required if col not in new_data.columns]
    if missing:
        raise ValueError(f"Missing required columns after migration: {missing}")
    
    return new_data

# Use the migration function
migrated_data = migrate_data(your_old_data)
```

### 3. Update API Calls

```python
# Replace old imports and calls
# OLD:
# from allocator.cluster_kmeans import main as cluster_kmeans
# result = cluster_kmeans(data, n_clusters=3)

# NEW:
import allocator
result = allocator.cluster(data, n_clusters=3, method='kmeans')
```

### 4. Update Result Handling

```python
# OLD: 
# result was a dictionary, tuple, or DataFrame

# NEW: Use structured result objects
result = allocator.cluster(data, n_clusters=3)

# Access structured data
labels = result.labels
centroids = result.centroids  
clustered_data = result.data
algorithm_info = result.metadata
```

### 5. Update CLI Scripts

```bash
# Replace old CLI calls in scripts/automation
# OLD: python -m allocator.cluster_kmeans data.csv -n 3
# NEW: allocator cluster data.csv --clusters 3
```

## 🔍 Common Migration Issues

### Issue 1: Column Name Errors

**Error:**
```
ValueError: Missing required columns: ['longitude', 'latitude']
```

**Solution:**
```python
# Check current column names
print(data.columns.tolist())

# Rename as needed
data = data.rename(columns={'start_long': 'longitude', 'start_lat': 'latitude'})
```

### Issue 2: Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'allocator.cluster_kmeans'
```

**Solution:**
```python
# OLD import
# from allocator.cluster_kmeans import main

# NEW import  
import allocator
result = allocator.cluster(data, n_clusters=3)
```

### Issue 3: Result Access

**Error:**
```
KeyError: 'labels'  # or TypeError: 'ClusterResult' object is not subscriptable
```

**Solution:**
```python
# OLD: result was dict
# labels = result['labels']

# NEW: result is structured object
labels = result.labels
data_with_clusters = result.data
```

## 📚 Additional Resources

- **API Examples**: [docs/API_EXAMPLES.md](API_EXAMPLES.md)
- **Full Documentation**: https://geosensing.github.io/allocator/
- **GitHub Issues**: Report migration problems at https://github.com/geosensing/allocator/issues

## 💡 Migration Tips

1. **Start with data format** - Fix column names first
2. **Test incrementally** - Migrate one function at a time  
3. **Use the Python API** - More flexible than CLI for complex workflows
4. **Leverage new features** - Rich metadata and structured results
5. **Check performance** - v1.0 should be faster for most use cases

Need help? Open an issue on GitHub with your specific migration challenge!