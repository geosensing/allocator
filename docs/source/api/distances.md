# Distance Calculation API

Distance matrix computation and geographic distance calculations.

## Main Functions

```{eval-rst}
.. autofunction:: allocator.get_distance_matrix
```

## Distance Modules

### Factory Module
```{eval-rst}
.. automodule:: allocator.distances.factory
   :members:
   :undoc-members:
   :show-inheritance:
```

### Euclidean Distance
```{eval-rst}
.. automodule:: allocator.distances.euclidean
   :members:
   :undoc-members:
   :show-inheritance:
```

### Haversine Distance
```{eval-rst}
.. automodule:: allocator.distances.haversine
   :members:
   :undoc-members:
   :show-inheritance:
```

### External APIs
```{eval-rst}
.. automodule:: allocator.distances.external_apis
   :members:
   :undoc-members:
   :show-inheritance:
```

## Usage Examples

### Basic Distance Matrix

```python
import pandas as pd
import allocator

# Geographic locations
locations = pd.DataFrame({
    'longitude': [100.5, 100.6, 100.7],
    'latitude': [13.7, 13.8, 13.9],
})

# Calculate distance matrix
distances = allocator.get_distance_matrix(
    data=locations,
    method='haversine'
)

print(f"Distance matrix shape: {distances.shape}")
print(f"Distance from point 0 to point 1: {distances[0,1]:.2f}km")
```

### Performance Comparison

```python
import time

methods = ['euclidean', 'haversine']
for method in methods:
    start = time.time()
    distances = allocator.get_distance_matrix(locations, method=method)
    elapsed = time.time() - start
    print(f"{method}: {elapsed:.3f}s")
```

## Distance Methods

### Euclidean Distance
- **Method**: `euclidean`
- **Formula**: Straight-line distance in Cartesian coordinates
- **Speed**: Fastest
- **Accuracy**: Approximate for geographic coordinates
- **Best for**: Quick estimates, large datasets, non-geographic data

```python
# Fast approximate distances
distances = allocator.get_distance_matrix(data, method='euclidean')
```

### Haversine Distance  
- **Method**: `haversine`
- **Formula**: Great-circle distance on Earth's surface
- **Speed**: Fast
- **Accuracy**: High for geographic coordinates
- **Best for**: Most geographic applications (recommended)

```python
# Accurate geographic distances
distances = allocator.get_distance_matrix(data, method='haversine')
```

### OSRM Driving Distance
- **Method**: `osrm`
- **Data source**: OpenStreetMap road networks
- **Speed**: Moderate (API calls)
- **Accuracy**: Realistic driving distances
- **Requirements**: Internet connection, OSRM server access

```python
# Realistic driving distances
distances = allocator.get_distance_matrix(data, method='osrm')
```

### Google Maps Distance
- **Method**: `googlemaps`  
- **Data source**: Google Maps road data
- **Speed**: Slow (API calls, rate limits)
- **Accuracy**: High-quality driving distances
- **Requirements**: Google Maps API key, billing account

```python
# High-quality driving distances (requires API key)
distances = allocator.get_distance_matrix(
    data, 
    method='googlemaps',
    api_key='your_api_key'
)
```

## API Configuration

### OSRM Configuration
```python
# Custom OSRM server
distances = allocator.get_distance_matrix(
    data,
    method='osrm',
    osrm_url='http://your-osrm-server:5000'
)
```

### Google Maps Configuration
```python
# Google Maps with API key
import os
os.environ['GOOGLEMAPS_API_KEY'] = 'your_api_key'

distances = allocator.get_distance_matrix(data, method='googlemaps')
```

## Return Format

All distance methods return a NumPy array where:
- `distances[i,j]` = distance from point i to point j
- Diagonal elements are 0 (distance from point to itself)
- Matrix is symmetric for undirected distances
- Units are always kilometers

## Performance Characteristics

| Method | Speed | Accuracy | Use Case |
|--------|-------|----------|----------|
| euclidean | ★★★★★ | ★★☆☆☆ | Quick estimates, large datasets |
| haversine | ★★★★☆ | ★★★★★ | Geographic analysis (recommended) |
| osrm | ★★★☆☆ | ★★★★☆ | Realistic routing |
| googlemaps | ★☆☆☆☆ | ★★★★★ | Production routing applications |

## Integration with Other Functions

Distance methods are used automatically by other allocator functions:

```python
# Clustering with specific distance method
clusters = allocator.cluster(data, distance='haversine')

# Routing with specific distance method  
route = allocator.shortest_path(data, distance='euclidean')

# Assignment with specific distance method
assignments = allocator.assign(points, workers, distance='osrm')
```

## Error Handling

```python
try:
    distances = allocator.get_distance_matrix(data, method='googlemaps')
except Exception as e:
    print(f"API error: {e}")
    # Fallback to local method
    distances = allocator.get_distance_matrix(data, method='haversine')
```

## Advanced Usage

### Custom Distance Functions
```python
def custom_manhattan_distance(data):
    """Manhattan distance in kilometers."""
    # Convert to UTM coordinates for accurate metric calculation
    # ... custom implementation ...
    pass

# Use custom function with clustering
clusters = allocator.cluster(data, distance=custom_manhattan_distance)
```

### Batch Processing
```python
# Process large datasets in chunks
def batch_distance_matrix(data, chunk_size=100):
    """Calculate distance matrix in batches."""
    n = len(data)
    distances = np.zeros((n, n))
    
    for i in range(0, n, chunk_size):
        chunk = data.iloc[i:i+chunk_size]
        chunk_distances = allocator.get_distance_matrix(chunk)
        distances[i:i+len(chunk), i:i+len(chunk)] = chunk_distances
    
    return distances
```