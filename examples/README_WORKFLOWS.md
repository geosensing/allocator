# Allocator Examples - End-to-End Workflows

This directory contains comprehensive examples demonstrating the complete allocator v1.0 workflow using **real geographic data** from Delhi, India and Chonburi, Thailand road networks.

## 🎯 Complete Workflow Examples

### 1. **real_world_workflow.py** - Production Workflow
```bash
uv run python real_world_workflow.py
```

**What it demonstrates:**
- Complete analysis pipeline using actual OpenStreetMap road data
- Clustering analysis (K-means with euclidean/haversine distances)
- Route optimization (TSP with OR-Tools)
- Assignment optimization (distance-based depot assignment)
- Performance metrics and timing analysis

**Real-world applications:**
- Road maintenance zone planning
- Emergency response depot placement  
- Delivery service territory optimization
- Infrastructure inspection scheduling

**Output:** Performance metrics and analysis results for both cities

---

### 2. **algorithm_comparison.py** - Performance Analysis
```bash
uv run python algorithm_comparison.py
```

**What it generates:**
- **PNG visualizations** (like `chonburi-gm-11.png` style files)
- **CSV result files** with algorithm outputs
- **Performance comparison charts**
- **Statistical analysis summaries**

**Generated files:**
```
algorithm_comparison_output/
├── visualizations/
│   ├── Delhi_clustering_comparison.png
│   ├── Delhi_routing_comparison.png
│   ├── Delhi_distance_comparison.png
│   ├── Chonburi_clustering_comparison.png
│   ├── Chonburi_routing_comparison.png
│   └── Chonburi_distance_comparison.png
├── csv_results/
│   ├── Delhi_euclidean_5clusters_clusters.csv
│   ├── Delhi_haversine_15points_route.csv
│   ├── Chonburi_euclidean_distance_matrix.csv
│   └── [32 more CSV files...]
└── performance_metrics/
    ├── algorithm_performance_summary.csv
    └── summary.json
```

**Comparison analysis:**
- Multiple clustering algorithms (K-means with different distance metrics)
- TSP routing with varying problem sizes (5-15 points)
- Distance calculation methods (Euclidean vs Haversine)
- Performance scaling analysis

---

### 3. **cli_workflow_demo.py** - Command Line Interface
```bash
uv run python cli_workflow_demo.py
```

**What it demonstrates:**
- Complete CLI functionality with real road network data
- All major commands with actual outputs
- File format handling (CSV input/output, JSON)
- Advanced workflow combinations
- Production usage patterns

**CLI commands tested:**
```bash
# Clustering
allocator cluster kmeans data.csv --n-clusters 3 --distance haversine

# Routing  
allocator route ortools points.csv --output route.csv

# Assignment
allocator sort locations.csv --workers depots.csv --format json
```

---

## 📊 Real Data Sources

### Delhi Road Network (`delhi-roads-1k.csv`)
- **Source:** OpenStreetMap
- **Coverage:** 1,000 road segments in Delhi, India
- **Coordinates:** 28.414°-28.880°N, 76.870°-77.329°E
- **Road types:** Primary, secondary, tertiary, trunk roads
- **Real locations:** Mahatma Gandhi Road, Outer Circle, Windsor Place, etc.

### Chonburi Road Network (`chonburi-roads-1k.csv`)  
- **Source:** OpenStreetMap
- **Coverage:** 1,000 road segments in Chonburi Province, Thailand
- **Coordinates:** 12.623°-13.578°N, 100.867°-101.648°E
- **Road types:** Primary, secondary, tertiary, trunk roads
- **Real locations:** Sukhumvit Road (ถนนสุขุมวิท), major highways

## 🚀 Quick Start Guide

### Basic Workflow
```bash
# 1. Install allocator with all dependencies
uv add allocator

# 2. Run complete real-world analysis
uv run python real_world_workflow.py

# 3. Generate visualizations and comparisons  
uv run python algorithm_comparison.py

# 4. Test CLI functionality
uv run python cli_workflow_demo.py
```

### Simple API Usage
```python
import allocator
import pandas as pd

# Load real road data
roads = pd.read_csv("delhi-roads-1k.csv")
points = pd.DataFrame({
    'longitude': roads['start_long'].head(50),
    'latitude': roads['start_lat'].head(50)
})

# Cluster into maintenance zones
clusters = allocator.cluster(points, n_clusters=5, distance='haversine')

# Find optimal inspection route
route = allocator.shortest_path(points.head(10), method='ortools')

# Assign to service depots
depots = pd.DataFrame({
    'longitude': [77.1, 77.2], 
    'latitude': [28.6, 28.7]
})
assignments = allocator.assign_to_closest(points, depots)
```

## 🎨 Visualization Examples

The algorithm comparison script generates visualization files similar to those in the examples directory:

### Generated Visualizations
- **Clustering comparisons:** Performance vs cluster count, method comparisons
- **Routing analysis:** TSP solution time vs problem size, efficiency metrics
- **Distance method comparisons:** Euclidean vs Haversine accuracy and speed
- **Performance summaries:** Algorithm timing and success rates

### File Naming Convention
- `{City}_{algorithm}_{parameters}_{type}.{ext}`
- Examples: `Delhi_euclidean_5clusters_clusters.csv`, `Chonburi_routing_comparison.png`

## 📈 Performance Metrics

### Typical Results (sample from recent runs)
```
🏙️ Delhi Results Summary:
  • Dataset: 1,000 road segments
  • Clustering: 5 zones in 0.05s
  • Route optimization: 146.2km route in 0.18s
  • Assignment: Avg 24.4km distance in 0.03s

🏙️ Chonburi Results Summary:  
  • Dataset: 1,000 road segments
  • Clustering: 5 zones in 0.03s
  • Route optimization: 268.0km route in 0.00s
  • Assignment: Avg 15.2km distance in 0.02s
```

## 🏗️ Production Applications

### Urban Planning
- **Zone creation:** Maintenance districts, service areas
- **Route optimization:** Inspection schedules, service routes
- **Resource allocation:** Depot placement, capacity planning

### Logistics & Delivery
- **Territory management:** Driver assignments, delivery zones
- **Route planning:** Last-mile optimization, pickup/delivery
- **Network design:** Hub placement, capacity planning

### Emergency Services
- **Response zones:** Ambulance, fire station coverage
- **Resource deployment:** Equipment placement, staffing
- **Route optimization:** Emergency response paths

## 📝 Next Steps

1. **Scale up:** Use full datasets (increase sample sizes)
2. **Integrate APIs:** Add OSRM/Google Maps for real road distances
3. **Add visualization:** Use Folium for interactive maps
4. **Custom algorithms:** Implement domain-specific optimizations

---

**Ready for production use!** All examples demonstrate real-world scenarios with actual geographic data and measurable performance improvements.