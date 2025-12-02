# Assignment API

Assign geographic points to closest workers, centers, or service locations.

## Main Functions

```{eval-rst}
.. autofunction:: allocator.assign
```

## Core Assignment Module

```{eval-rst}
.. automodule:: allocator.api.distance
   :members:
   :undoc-members:
   :show-inheritance:
```

## Usage Examples

### Basic Point Assignment

```python
import pandas as pd
import allocator

# Customer locations
customers = pd.DataFrame({
    'longitude': [100.5, 100.6, 100.7, 100.8],
    'latitude': [13.7, 13.8, 13.9, 14.0],
    'customer_id': ['C1', 'C2', 'C3', 'C4']
})

# Service centers  
centers = pd.DataFrame({
    'longitude': [100.55, 100.75],
    'latitude': [13.75, 13.85], 
    'center_id': ['North', 'South']
})

# Assign customers to closest centers
assignments = allocator.assign(
    points=customers,
    workers=centers,
    distance='haversine'
)

print("Assignment results:")
for _, row in assignments.iterrows():
    print(f"{row['customer_id']} → {row['center_id']} ({row['distance']:.2f}km)")
```

### Assignment with Capacity Constraints

```python
# Centers with capacity limits
centers_with_capacity = pd.DataFrame({
    'longitude': [100.55, 100.75],
    'latitude': [13.75, 13.85],
    'center_id': ['North', 'South'],
    'capacity': [2, 2]  # Maximum assignments per center
})

# Assign with capacity constraints
assignments = allocator.assign(
    points=customers,
    workers=centers_with_capacity,
    distance='haversine',
    capacity_column='capacity'
)

# Check capacity utilization
for center in centers_with_capacity['center_id']:
    assigned = assignments[assignments['center_id'] == center]
    capacity = centers_with_capacity[
        centers_with_capacity['center_id'] == center
    ]['capacity'].iloc[0]
    print(f"{center}: {len(assigned)}/{capacity} capacity used")
```

## Assignment Options

### Distance Methods
- **haversine**: Geographic distance (recommended)
- **euclidean**: Straight-line distance (fast)
- **osrm**: Driving distance via OSRM API
- **googlemaps**: Driving distance via Google Maps API

### Capacity Handling
- **Simple assignment**: Each point assigned to closest worker
- **Capacity constraints**: Respect maximum assignments per worker
- **Load balancing**: Distribute assignments evenly

## Data Requirements

### Points (customers/tasks)
Required columns:
- `longitude`: Point longitude
- `latitude`: Point latitude

Optional columns:
- `point_id`: Unique identifier (auto-generated if missing)

### Workers (centers/service locations)
Required columns:
- `longitude`: Worker/center longitude  
- `latitude`: Worker/center latitude

Optional columns:
- `worker_id`: Unique identifier (auto-generated if missing)
- `capacity`: Maximum assignments (unlimited if not specified)

## Return Format

The `assign` function returns a DataFrame with:

- All original point columns
- All original worker columns (prefixed with `worker_`)  
- `worker_id`: Assigned worker identifier
- `distance`: Distance to assigned worker
- `assignment_rank`: Rank of this assignment (1 = closest)

## Performance

Assignment operations scale well:
- **Small datasets (≤100 points)**: Instant results
- **Medium datasets (100-1000 points)**: Sub-second performance
- **Large datasets (1000+ points)**: Linear scaling

For very large datasets, consider:
- Using euclidean distance for speed
- Pre-filtering points by geographic region
- Batch processing in smaller chunks

## Business Applications

### Service Territory Planning
```python
# Assign customers to sales representatives
territories = allocator.assign(customers, sales_reps)
```

### Emergency Services
```python  
# Assign incidents to closest fire stations
assignments = allocator.assign(incidents, fire_stations)
```

### Logistics Optimization
```python
# Assign deliveries to distribution centers
logistics = allocator.assign(deliveries, warehouses, capacity_column='daily_capacity')
```