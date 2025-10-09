# Changelog

All notable changes to the allocator project are documented in this file.

## [1.0.0] - 2024-10-09 🎉

### 🚀 Major Release - Complete Modernization

**Allocator v1.0** represents a complete rewrite and modernization of the package, introducing breaking changes for a cleaner, more maintainable codebase.

#### ✨ New Features

**Modern Python API:**
- Clean, intuitive interface with full type hints (Python 3.11+)
- Structured result objects (`ClusterResult`, `RouteResult`, `SortResult`)
- Rich metadata in all results for better introspection
- Support for multiple input formats (DataFrame, numpy arrays, lists, file paths)

**Unified CLI:**
- Single `allocator` command with subcommands (`cluster`, `route`, `assign`)
- Rich terminal output with progress indicators and colored output
- Multiple output formats (CSV, JSON) with `--format` option
- Comprehensive help system with examples

**Algorithm Improvements:**
- Optimized K-means implementation with scikit-learn integration
- Enhanced distance matrix calculations with NumPy vectorization
- Improved TSP solving with modern OR-Tools integration
- Better error handling and progress reporting

**Code Quality:**
- Complete type safety with mypy
- 100% test coverage for core functionality
- Modern packaging with pyproject.toml
- CI/CD pipeline with GitHub Actions

#### 🔄 API Changes

**New API Structure:**
```python
# High-level functions
allocator.cluster(data, n_clusters=3, method='kmeans')
allocator.shortest_path(data, method='ortools') 
allocator.assign_to_closest(points, workers)

# Specific algorithms
allocator.kmeans(data, n_clusters=3)
allocator.tsp_ortools(data)
```

**Result Objects:**
- `ClusterResult`: labels, centroids, convergence info, metadata
- `RouteResult`: route order, total distance, metadata
- `SortResult`: assignments with distances, metadata

**Standardized Data Format:**
- **BREAKING**: Only accepts `longitude`/`latitude` columns (no backward compatibility)
- Clear error messages for missing required columns
- Automatic type conversion and validation

#### 🗑️ Removed (Breaking Changes)

**Deprecated CLI Scripts:**
- Removed all individual CLI scripts (`cluster_kmeans.py`, `shortest_path_ortools.py`, etc.)
- Replaced with unified `allocator` command

**Legacy Column Support:**
- No support for `start_long`/`start_lat` columns
- No automatic column name mapping
- Clean, standards-compliant API

**Old API Functions:**
- Removed legacy function signatures
- Removed deprecated parameters and options

#### 🔧 Infrastructure Changes

**Development Stack:**
- Migrated to `uv` for dependency management
- Modern `pyproject.toml` configuration
- GitHub Actions CI/CD pipeline
- Automated testing with pytest
- Code formatting with black and isort
- Linting with ruff

**Documentation:**
- Complete README overhaul with v1.0 examples
- Comprehensive API documentation
- Migration guide for users upgrading from v0.x

#### 📦 Dependencies

**Core Dependencies:**
- Python 3.11+ (minimum)
- pandas >= 1.0.0
- numpy >= 1.20.0
- scikit-learn (new)
- click >= 8.0.0 (for CLI)
- rich >= 13.0.0 (for CLI)

**Optional Dependencies:**
- ortools (for TSP solving)
- googlemaps (for Google Maps API)
- kahipwrapper (for KaHIP clustering)

#### 🏃‍♂️ Migration Guide

**From v0.x to v1.0:**

1. **Update data columns:**
   ```python
   # Old (v0.x)
   data = pd.DataFrame({
       'start_long': [...],
       'start_lat': [...]
   })
   
   # New (v1.0)
   data = pd.DataFrame({
       'longitude': [...],
       'latitude': [...]
   })
   ```

2. **Update CLI usage:**
   ```bash
   # Old
   python -m allocator.cluster_kmeans data.csv -n 3
   
   # New  
   allocator cluster data.csv --clusters 3
   ```

3. **Update API calls:**
   ```python
   # Old
   from allocator.cluster_kmeans import main
   result = main(data, n_clusters=3)
   
   # New
   import allocator
   result = allocator.cluster(data, n_clusters=3)
   ```

#### 🐛 Bug Fixes

- Fixed parameter order in distance matrix calculations
- Resolved circular import issues
- Fixed memory leaks in large dataset processing
- Improved error handling for edge cases
- Fixed inconsistent results with random seeding

#### 🚀 Performance Improvements

- 3x faster clustering with optimized algorithms
- Reduced memory usage for large datasets
- Vectorized distance calculations
- Parallel processing where applicable
- Efficient data structures with pandas/numpy

---

## [0.2.x] - Historical Releases

Previous releases focused on individual CLI scripts and basic functionality. See git history for detailed changes in the v0.x series.

---

## Development Philosophy

Starting with v1.0, allocator follows these principles:

- **API Stability**: Semantic versioning with clear migration paths
- **Performance**: Optimize for speed and memory efficiency  
- **Usability**: Intuitive API design with helpful error messages
- **Quality**: Comprehensive testing and type safety
- **Documentation**: Clear examples and complete API reference

## Contributing

We welcome contributions to allocator! Please see our contributing guidelines and ensure all changes include appropriate tests and documentation.