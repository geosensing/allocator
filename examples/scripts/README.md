# Allocator Example Scripts

This directory contains comprehensive workflow scripts demonstrating allocator v1.0 functionality using real geographic data.

## 🎯 Available Scripts

### 1. **quick_start.py** - Basic API Introduction
```bash
uv run python quick_start.py
```

**Purpose:** Simple demonstration of core allocator functions  
**Data:** Synthetic Bangkok area coordinates  
**Output:** Console output showing clustering, routing, and assignment results  
**Runtime:** ~1-2 seconds  

**What it shows:**
- Basic clustering with k-means
- TSP route optimization  
- Distance-based assignment
- Simple API usage patterns

---

### 2. **real_world_workflow.py** - Complete Production Workflow
```bash
uv run python real_world_workflow.py
```

**Purpose:** End-to-end analysis using real road network data  
**Data:** Delhi and Chonburi road networks (1000+ segments each)  
**Output:** Console analysis with performance metrics  
**Runtime:** ~5-10 seconds  

**What it demonstrates:**
- Clustering analysis with multiple distance methods
- Route optimization with performance metrics
- Assignment optimization with depot placement
- Distance matrix calculations and comparisons
- Real-world performance benchmarks

---

### 3. **algorithm_comparison.py** - Comprehensive Analysis & Visualization
```bash
uv run python algorithm_comparison.py
```

**Purpose:** Generate organized visualizations and comparison reports  
**Data:** Delhi and Chonburi road networks  
**Output:** Timestamped directory structure with PNG charts, CSV data, HTML reports  
**Runtime:** ~30-60 seconds  

**Generated outputs:**
```
../outputs/YYYY-MM-DD_HH-MM/
├── delhi/
│   ├── clustering/
│   │   ├── data/*.csv           # Clustering results
│   │   ├── visualizations/*.png # Performance charts
│   │   └── reports/*.html       # Analysis reports
│   └── routing/[same structure]
├── chonburi/[same structure]
└── comparisons/
    ├── data/analysis_summary.json
    ├── visualizations/comparison_charts.png
    └── reports/executive_summary.html
```

---

### 4. **distance_methods.py** - Distance Calculation Demo
```bash
uv run python distance_methods.py
```

**Purpose:** Compare different distance calculation methods  
**Data:** Sample city coordinates  
**Output:** Distance method comparisons and recommendations  
**Runtime:** <1 second  

---

### 5. **cli_workflow_demo.py** - Command Line Interface Demo
```bash
uv run python cli_workflow_demo.py
```

**Purpose:** Demonstrate CLI functionality with real data  
**Data:** Creates temporary datasets from road networks  
**Output:** CLI command examples and organized temporary files  
**Runtime:** ~10-20 seconds  

---

## 🚀 Usage Patterns

### Quick Start
```bash
# Basic introduction
uv run python quick_start.py

# See real-world performance  
uv run python real_world_workflow.py
```

### Generate Comprehensive Analysis
```bash
# Create full analysis with visualizations
uv run python algorithm_comparison.py

# Results will be in ../outputs/latest/
```

### CLI Testing
```bash
# Test command-line interface
uv run python cli_workflow_demo.py

# Then try actual CLI commands:
uv run allocator cluster kmeans ../inputs/delhi-roads-1k.csv --n-clusters 5
```

## 📊 Output Organization

### Console Output Scripts
- `quick_start.py` - Basic console demo
- `distance_methods.py` - Distance comparison
- `real_world_workflow.py` - Performance analysis

### File Generation Scripts  
- `algorithm_comparison.py` - Organized output structure with visualizations
- `cli_workflow_demo.py` - Temporary files and CLI examples

## 🛠️ Dependencies

All scripts use the same dependencies defined in `../../pyproject.toml`:

- **Core:** pandas, numpy, scikit-learn
- **Visualization:** matplotlib, seaborn  
- **Geographic:** utm, haversine
- **Optimization:** ortools
- **CLI:** click, rich

## 📈 Performance Expectations

### Typical Runtime (on modern hardware)

| Script | Sample Size | Runtime | Output Files |
|--------|-------------|---------|--------------|
| quick_start.py | 6 points | 1-2s | Console only |
| distance_methods.py | 4 cities | <1s | Console only |
| real_world_workflow.py | 80-100 points | 5-10s | Console only |
| cli_workflow_demo.py | 50 points | 10-20s | Temp files |
| algorithm_comparison.py | 80 points | 30-60s | 20+ files |

### Scaling Recommendations

- **Small datasets (≤50 points):** All scripts run quickly
- **Medium datasets (50-200 points):** Expect proportional runtime increase  
- **Large datasets (500+ points):** Consider sampling or parallel processing

## 🎯 Business Applications

### Use Cases by Script

**quick_start.py:**
- Learning the API
- Proof of concept development
- Integration testing

**real_world_workflow.py:**
- Performance validation
- Benchmark establishment  
- Production planning

**algorithm_comparison.py:**
- Research and development
- Method selection
- Executive reporting
- Academic/conference presentations

**CLI testing:**
- Automation development
- Batch processing setup
- Integration with existing tools

## 📝 Customization

### Modifying Sample Sizes
```python
# In any script, adjust sample_size parameter:
points, raw_data = load_and_prepare_data(city, sample_size=100)  # Default
points, raw_data = load_and_prepare_data(city, sample_size=200)  # Larger analysis
```

### Adding New Cities
1. Add road network CSV to `../inputs/`
2. Update city list in script: `cities = ['Delhi', 'Chonburi', 'NewCity']`
3. Follow same CSV format as existing files

### Custom Analysis
```python
# Add new clustering parameters
n_clusters_list = [3, 5, 7, 10]  # Test more cluster counts
distance_methods = ['euclidean', 'haversine', 'osrm']  # Add OSRM
```

## 🔗 Next Steps

1. **Start with:** `quick_start.py` to understand basic functionality
2. **Validate with:** `real_world_workflow.py` for performance insights
3. **Generate reports:** `algorithm_comparison.py` for comprehensive analysis
4. **Scale up:** Modify sample sizes and add new datasets
5. **Integrate:** Use CLI commands in production workflows

Ready for production deployment and further development!