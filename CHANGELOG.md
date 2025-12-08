# Changelog

All notable changes to the allocator project are documented in this file.

## [1.1.0] - 2024-12-08 🚀

### ✨ New Features

**Interactive Geographic Visualizations:**
- Added `plot_clusters_interactive()` for interactive K-means clustering maps with folium
- Added `plot_route_interactive()` for interactive TSP route visualization with real maps
- Enhanced geographic context with OpenStreetMap tiles and zoom/pan capabilities
- Support for polyline-encoded routes from OSRM and Google Maps APIs
- Professional HTML output suitable for presentations and web sharing

**Enhanced Machine Learning Integration:**
- Introduced `CustomKMeans` class extending sklearn's KMeans with custom distance metrics
- Seamless fallback to pure Python implementation when sklearn unavailable
- Optimized performance while maintaining compatibility with haversine, OSRM, and Google Maps distances
- Improved convergence detection and reproducibility with random_state support

**Dependency Management Improvements:**
- Reorganized optional dependencies into logical groups: `algorithms`, `geo`, `dev`, `test`, `docs`
- Configured deptry for proper dependency validation with PEP 621 support
- Enhanced optional dependency handling with clear error messages
- Streamlined installation with `pip install 'allocator[geo]'` for mapping features

### 🔧 Code Quality & Performance

**Linting & Standards:**
- Fixed all ruff linting errors across entire codebase (58+ issues resolved)
- Enhanced code style consistency with proper whitespace handling
- Added `strict=` parameters to `zip()` calls for safety
- Improved variable naming and removed unused assignments

**Testing & Reliability:**
- Maintained 100% test coverage with 72 passing tests
- Enhanced K-means reproducibility testing for sklearn integration
- Improved test robustness for label permutation handling
- Validated compatibility across Python 3.11, 3.12, and 3.13

**Documentation & Examples:**
- Added comprehensive interactive visualization demo script
- Enhanced example scripts with proper error handling
- Improved docstring quality and type annotations
- Created professional HTML output examples for demos

### 🛠️ Technical Improvements

**Algorithm Optimizations:**
- Hybrid sklearn/custom K-means approach for best of both worlds
- Maintained geographic accuracy while leveraging sklearn optimizations
- Enhanced distance matrix calculations with vectorized operations
- Improved memory usage for large geographic datasets

**Infrastructure:**
- Enhanced CI/CD pipeline with automated quality checks
- Improved build process with uv and modern packaging
- Better dependency conflict resolution
- Streamlined release process with comprehensive testing

### 📦 Installation & Compatibility

**New Optional Groups:**
```bash
pip install 'allocator[algorithms]'  # scikit-learn for ML algorithms  
pip install 'allocator[geo]'         # folium + polyline for interactive maps
pip install 'allocator[all]'         # all optional features
```

**Maintained Compatibility:**
- All existing APIs remain unchanged
- No breaking changes for current users
- Backward compatible with v1.0.0 usage patterns

### 🐛 Bug Fixes

- Resolved dependency conflicts in development environment
- Fixed inconsistent K-means results between implementations
- Improved error handling for edge cases in clustering
- Enhanced stability for large geographic datasets

---

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