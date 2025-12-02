# Clustering API

Geographic point clustering for task allocation and zone creation.

## Main Functions

```{eval-rst}
.. autofunction:: allocator.cluster
```

## Core Clustering Module

```{eval-rst}
.. automodule:: allocator.api.cluster
   :members:
   :undoc-members:
   :show-inheritance:
```

## Usage Examples

### Basic K-means Clustering

```python
import pandas as pd
import allocator

# Geographic data
data = pd.DataFrame({
    'longitude': [100.5, 100.6, 100.7, 100.8],
    'latitude': [13.7, 13.8, 13.9, 14.0],
})

# Create 2 clusters using haversine distance
result = allocator.cluster(
    data=data,
    n_clusters=2, 
    distance='haversine',
    algorithm='kmeans'
)

print(f"Created {result['n_clusters']} clusters")
print(result['data'][['longitude', 'latitude', 'cluster']])
```

### Distance Methods

- **euclidean**: Fast straight-line distance
- **haversine**: Accurate geographic distance  
- **custom**: User-defined distance functions

### Algorithm Options

- **kmeans**: K-means clustering (default, balanced clusters)
- **custom**: Custom sklearn-compatible algorithms

## Return Format

The `cluster` function returns a dictionary with:

- `data`: DataFrame with original data plus `cluster` column
- `n_clusters`: Number of clusters created
- `algorithm`: Algorithm used
- `distance`: Distance method used
- `metadata`: Additional clustering information