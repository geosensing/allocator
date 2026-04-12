# allocator

[![PyPI version](https://img.shields.io/pypi/v/allocator.svg)](https://pypi.python.org/pypi/allocator)
[![Downloads](https://pepy.tech/badge/allocator)](https://pepy.tech/project/allocator)
[![CI](https://github.com/geosensing/allocator/actions/workflows/ci.yml/badge.svg)](https://github.com/geosensing/allocator/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-github.io-blue)](https://geosensing.github.io/allocator/)

Field teams, delivery services, and survey organizations waste time and money on inefficient routes. When you have 100+ locations to visit, manual planning fails. Allocator solves this.

## What It Does

- **Cluster**: Divide locations into balanced work zones
- **Route**: Find the shortest path through locations (TSP)
- **Assign**: Match locations to nearest workers or depots
- **Random Walk**: Generate survey itineraries on road networks

## Install

```bash
pip install allocator
```

## Python API

### Cluster locations into zones

```python
import allocator
import pandas as pd

locations = pd.DataFrame({
    'longitude': [100.501, 100.506, 100.510, 100.515, 100.520],
    'latitude': [13.756, 13.759, 13.763, 13.768, 13.772]
})

result = allocator.cluster(locations, n_clusters=2)
print(result.labels)  # [0 0 0 1 1]
```

### Find shortest route

```python
route = allocator.shortest_path(locations, method='ortools')
print(route.route)  # [0, 1, 2, 4, 3, 0]
```

### Assign to nearest depot

```python
depots = pd.DataFrame({
    'longitude': [100.50, 100.52],
    'latitude': [13.75, 13.77]
})

assignments = allocator.assign_to_closest(locations, depots)
print(assignments.data['assigned_worker'].tolist())  # [0, 0, 1, 1, 1]
```

### Generate random walk itineraries

```python
import networkx as nx

# Load road network graph (from OSMnx or similar)
G = nx.read_graphml("road_network.graphml")

result = allocator.random_walk(G, n_walks=10, walk_length_m=5000)
print(result.data)  # DataFrame with waypoints
```

## CLI

```bash
allocator cluster kmeans locations.csv -n 5 -o zones.csv
allocator route tsp locations.csv --method ortools -o route.csv
allocator sort locations.csv --workers depots.csv -o assignments.csv
allocator random-walk road_network.graphml -n 10 -l 5000 -o waypoints.csv
```

## Documentation

- [Full Documentation](https://geosensing.github.io/allocator/)
- [API Reference](https://geosensing.github.io/allocator/api/clustering.html)

## License

MIT
