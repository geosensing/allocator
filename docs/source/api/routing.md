# Routing API

Optimal path finding and route optimization for geographic points.

## Main Functions

```{eval-rst}
.. autofunction:: allocator.shortest_path
```

## Core Routing Module

```{eval-rst}
.. automodule:: allocator.api.route
   :members:
   :undoc-members:
   :show-inheritance:
```

## Routing Algorithms Module

```{eval-rst}
.. automodule:: allocator.core.routing
   :members:
   :undoc-members:
   :show-inheritance:
```

## Usage Examples

### Basic Route Optimization

```python
import pandas as pd
import allocator

# Delivery locations
locations = pd.DataFrame({
    'longitude': [100.5, 100.6, 100.7, 100.8],
    'latitude': [13.7, 13.8, 13.9, 14.0],
    'stop_id': ['A', 'B', 'C', 'D']
})

# Find optimal route using OR-Tools
route = allocator.shortest_path(
    data=locations,
    method='ortools',
    distance='haversine'
)

print(f"Total distance: {route['total_distance']:.2f}km")
print("Route order:")
for i, stop in enumerate(route['data']['stop_id']):
    print(f"  {i+1}. {stop}")
```

### Advanced Routing Options

```python
# Route optimization with custom start/end points
route = allocator.shortest_path(
    data=locations,
    method='ortools',
    start_location=0,  # Start at first location
    end_location=0,    # Return to start (round trip)
    distance='haversine',
    time_limit=10      # 10 second optimization limit
)
```

## Routing Methods

### OR-Tools Solver
- **Method**: `ortools`
- **Performance**: Optimal solutions, fastest for medium datasets
- **Best for**: Production applications, balanced performance/quality

### Nearest Neighbor
- **Method**: `nearest`  
- **Performance**: Fast heuristic, approximate solutions
- **Best for**: Quick estimates, large datasets

### Christofides Algorithm
- **Method**: `christofides`
- **Performance**: Optimal solutions, slower
- **Requires**: `pip install "allocator[algorithms]"`
- **Best for**: Small datasets requiring optimal solutions

## Distance Methods

All routing methods support multiple distance calculations:

- **haversine**: Geographic great-circle distance (recommended)
- **euclidean**: Straight-line distance (fast approximation)
- **osrm**: Driving distance via OSRM API
- **googlemaps**: Driving distance via Google Maps API

## Return Format

The `shortest_path` function returns a dictionary with:

- `data`: DataFrame with route order and distances
- `total_distance`: Total route distance in kilometers
- `method`: Algorithm used
- `distance`: Distance calculation method
- `metadata`: Algorithm-specific information (iterations, solve time, etc.)

## Performance Considerations

- **Small problems (≤15 points)**: All methods perform well
- **Medium problems (15-50 points)**: OR-Tools recommended  
- **Large problems (50+ points)**: Consider nearest neighbor or sampling
- **API rate limits**: Use haversine/euclidean for development