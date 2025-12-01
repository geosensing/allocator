# Allocator Analysis Run - 2025-12-01 12:57

## 📁 Directory Structure

```
2025-12-01_12-57/
├── delhi/
│   ├── clustering/
│   │   ├── data/           # CSV files with clustering results
│   │   ├── visualizations/ # PNG performance charts  
│   │   └── reports/        # HTML detailed analysis
│   ├── routing/
│   │   ├── data/           # TSP solution CSV files
│   │   ├── visualizations/ # Route performance charts
│   │   └── reports/        # HTML routing analysis
│   └── assignments/        # (Future: assignment analysis)
├── chonburi/
│   └── [same structure as delhi]
└── comparisons/
    ├── data/               # Cross-city comparison data
    ├── visualizations/     # Comparison charts
    └── reports/            # Executive summary report
```

## 🎯 Key Files

- **Executive Summary:** `comparisons/reports/executive_summary.html`
- **City Reports:** `[city]/[analysis]/reports/[city]_[analysis]_report.html`
- **Performance Data:** `comparisons/data/analysis_summary.json`
- **Visualizations:** `[city]/[analysis]/visualizations/*.png`

## 📊 Analysis Overview

This run analyzed road network data for Delhi, India and Chonburi, Thailand using:

- **Clustering:** K-means with euclidean and haversine distance methods
- **Routing:** TSP optimization using OR-Tools  
- **Distance Methods:** Comparative analysis of calculation methods

## 🚀 Next Steps

1. View executive summary for high-level insights
2. Review city-specific reports for detailed analysis
3. Use CSV data files for further processing
4. Scale analysis to larger datasets or additional cities

## 🔗 Links

- [Executive Summary](comparisons/reports/executive_summary.html)
- [Delhi Analysis](delhi/)  
- [Chonburi Analysis](chonburi/)
- [Source Code](../scripts/)
