# Allocator Examples - Professional Demo Suite

This directory provides a complete demonstration suite for **allocator v1.0** using real-world geographic data and production-ready workflows.

## 🎯 Quick Start

```bash
# 1. Basic API introduction (1-2 seconds)
uv run python examples/scripts/quick_start.py

# 2. Real-world performance analysis (5-10 seconds)
uv run python examples/scripts/real_world_workflow.py

# 3. Generate comprehensive visualizations (30-60 seconds)
uv run python examples/scripts/algorithm_comparison.py

# View results
open examples/outputs/latest/comparisons/reports/executive_summary.html
```

## 📁 Directory Structure

```
examples/
├── inputs/                          # Source datasets
│   ├── delhi-roads-1k.csv          # Delhi, India road network (1000 segments)
│   ├── chonburi-roads-1k.csv       # Chonburi, Thailand road network (1000 segments)
│   └── README.md                   # Data source documentation
│
├── scripts/                        # Workflow demonstrations
│   ├── quick_start.py              # Basic API introduction
│   ├── real_world_workflow.py      # Complete performance analysis
│   ├── algorithm_comparison.py     # Comprehensive visualization generator
│   ├── distance_methods.py         # Distance calculation comparison
│   ├── cli_workflow_demo.py        # CLI interface demonstration
│   └── README.md                   # Script documentation
│
├── outputs/                        # Generated results (timestamped)
│   ├── YYYY-MM-DD_HH-MM/          # Analysis runs
│   │   ├── delhi/                  # Delhi analysis results
│   │   │   ├── clustering/         # K-means clustering analysis
│   │   │   │   ├── data/*.csv      # Clustering result datasets
│   │   │   │   ├── visualizations/*.png # Performance charts
│   │   │   │   └── reports/*.html  # Detailed HTML analysis
│   │   │   └── routing/            # TSP routing analysis
│   │   │       ├── data/*.csv      # Route solution datasets
│   │   │       ├── visualizations/*.png # Route performance charts
│   │   │       └── reports/*.html  # Routing analysis reports
│   │   ├── chonburi/               # Chonburi analysis (same structure)
│   │   ├── comparisons/            # Cross-city comparisons
│   │   │   ├── data/analysis_summary.json
│   │   │   └── reports/executive_summary.html
│   │   └── README.md               # Run documentation
│   └── latest/                     # Symlink to most recent analysis
│
└── README.md                       # This file
```

## 🌍 Real-World Data

### Delhi Road Network  
- **1,000 road segments** from OpenStreetMap
- **Major roads:** Mahatma Gandhi Road, Outer Circle, Grand Trunk Road
- **Coverage:** Central Delhi with diverse road types
- **Applications:** Urban planning, emergency services, logistics

### Chonburi Road Network
- **1,000 road segments** from OpenStreetMap  
- **Major roads:** Sukhumvit Road (ถนนสุขุมวิท), regional highways
- **Coverage:** Chonburi Province with coastal and inland areas
- **Applications:** Tourism logistics, industrial planning, transportation

## 🚀 Demonstration Workflows

### 1. Quick API Introduction
```bash
uv run python examples/scripts/quick_start.py
```
- **Purpose:** Learn basic allocator functionality
- **Runtime:** 1-2 seconds
- **Output:** Console demonstration of clustering, routing, assignment

### 2. Real-World Performance Analysis  
```bash
uv run python examples/scripts/real_world_workflow.py
```
- **Purpose:** Production performance validation
- **Runtime:** 5-10 seconds
- **Output:** Performance metrics using actual city data

### 3. Comprehensive Visualization Generation
```bash  
uv run python examples/scripts/algorithm_comparison.py
```
- **Purpose:** Research, reporting, executive presentations
- **Runtime:** 30-60 seconds
- **Output:** Professional visualization suite with 20+ files

**Generated files include:**
- 📊 **PNG visualizations:** Performance charts, comparison plots
- 📋 **CSV datasets:** Algorithm results, route solutions  
- 📄 **HTML reports:** Executive summaries, detailed analysis
- 🔧 **JSON summaries:** Machine-readable performance metrics

**💾 Intermediate File Preservation:**
All generated outputs (PNG charts, CSV data, HTML reports) are automatically preserved in timestamped directories under `examples/outputs/YYYY-MM-DD_HH-MM/` with organized structure by city and analysis type. This ensures all intermediate analysis files are retained for review, comparison, and further processing.

## 📊 Example Outputs

### Performance Metrics (typical results)
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

### Generated Visualization Files
- `delhi_clustering_analysis.png` - Clustering performance comparison
- `chonburi_routing_analysis.png` - TSP routing optimization charts
- `executive_summary.html` - Professional analysis report

### Business-Ready CSV Outputs
- `kmeans_euclidean_5clusters.csv` - Clustering assignments
- `tsp_ortools_15points.csv` - Optimized route solutions
- `analysis_summary.json` - Performance benchmarks

## 🎯 Business Applications

### Urban Planning
- **Zone Creation:** Maintenance districts, service areas
- **Infrastructure:** Inspection scheduling, resource allocation
- **Development:** New facility placement optimization

### Logistics & Delivery
- **Route Optimization:** Last-mile delivery, pickup scheduling
- **Territory Management:** Driver assignments, coverage areas
- **Network Design:** Hub placement, capacity planning

### Emergency Services
- **Response Zones:** Ambulance, fire station coverage
- **Resource Deployment:** Equipment placement, staffing
- **Evacuation Planning:** Route optimization, capacity analysis

### Research & Development
- **Algorithm Validation:** Performance benchmarking
- **Method Comparison:** Distance metrics, optimization approaches
- **Academic Research:** Geographic optimization, urban analytics

## 🛠️ Technical Details

### Dependencies
All dependencies are defined in `../../pyproject.toml`:
- **Core:** pandas, numpy, scikit-learn
- **Optimization:** ortools  
- **Visualization:** matplotlib, seaborn
- **Geographic:** utm, haversine, googlemaps
- **CLI:** click, rich

### Performance Characteristics
- **Small problems (≤50 points):** Sub-second execution
- **Medium problems (50-200 points):** 1-10 seconds
- **Large problems (200+ points):** 10+ seconds, consider sampling

### System Requirements  
- **Python:** 3.11+ (tested on 3.11-3.13)
- **Memory:** 2GB+ for large datasets
- **Storage:** 100MB for full analysis outputs
- **Network:** Optional for OSRM/Google Maps APIs

## 📈 Scaling Guidelines

### Development & Testing
```bash
# Quick validation (1-2 seconds)
uv run python examples/scripts/quick_start.py

# Performance testing (5-10 seconds)  
uv run python examples/scripts/real_world_workflow.py
```

### Production Analysis
```bash
# Comprehensive reporting (30-60 seconds)
uv run python examples/scripts/algorithm_comparison.py

# Custom CLI workflows
uv run allocator cluster kmeans examples/inputs/delhi-roads-1k.csv --n-clusters 7 --output results.csv
```

### Large-Scale Deployment
- Use CLI batch processing for multiple datasets
- Consider parallel processing for multiple cities
- Implement result caching for repeated analysis
- Scale visualization generation for executive reporting

## 🔗 Integration Examples

### Python API Integration
```python
import allocator
import pandas as pd

# Load real road data  
roads = pd.read_csv('examples/inputs/delhi-roads-1k.csv')
points = pd.DataFrame({
    'longitude': roads['start_long'],
    'latitude': roads['start_lat']  
})

# Production-ready analysis
clusters = allocator.cluster(points, n_clusters=5, distance='haversine')
route = allocator.shortest_path(points.head(10), method='ortools')
```

### CLI Integration
```bash
#!/bin/bash
# Production batch processing
for city in delhi chonburi; do
    allocator cluster kmeans examples/inputs/${city}-roads-1k.csv \
        --n-clusters 5 \
        --output results/${city}_zones.csv
done
```

### Dashboard Integration
```python
# Load analysis results for dashboard
import json
with open('examples/outputs/latest/comparisons/data/analysis_summary.json') as f:
    metrics = json.load(f)
    
# Display in web dashboard, monitoring system, etc.
```

## 🏆 Success Metrics

This demonstration suite validates:

- ✅ **Performance:** All algorithms complete within seconds for real-world data
- ✅ **Accuracy:** Haversine distance provides geographically accurate results  
- ✅ **Scalability:** Handles 1000+ point datasets efficiently
- ✅ **Usability:** Simple API with professional visualization output
- ✅ **Production-Ready:** Comprehensive error handling and documentation

## 📝 Next Steps

1. **Explore:** Run `uv run python examples/scripts/quick_start.py` to understand basic functionality
2. **Validate:** Use `uv run python examples/scripts/real_world_workflow.py` for performance insights  
3. **Generate:** Create professional reports with `uv run python examples/scripts/algorithm_comparison.py`
4. **Customize:** Modify scripts for your specific datasets and requirements
5. **Scale:** Implement in production systems using CLI or Python API

---

**🎉 Ready for production deployment!** This suite demonstrates production-ready geographic optimization using real-world data from major urban areas.