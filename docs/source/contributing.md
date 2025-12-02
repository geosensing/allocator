# Contributing to Allocator

Thank you for your interest in contributing to allocator! This guide will help you get started.

## Development Setup

### Prerequisites
- Python 3.11 or higher
- Git
- UV (recommended) or pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/geosensing/allocator.git
cd allocator
```

2. **Install dependencies** 
```bash
# With UV (recommended)
uv sync --all-extras

# Or with pip
pip install -e ".[complete]"
```

3. **Set up pre-commit hooks**
```bash
pre-commit install
```

## Code Standards

### Linting and Formatting
We use modern Python tooling:

```bash
# Linting and formatting with ruff
uv run ruff check .
uv run ruff format .

# Type checking with mypy  
uv run mypy allocator/

# Traditional tools (if preferred)
uv run black .
uv run isort .
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=allocator --cov-report=html

# Run specific test files
uv run pytest tests/api/test_cluster_api.py
```

### Documentation
```bash
# Build documentation locally
cd docs/
make html

# View documentation
open build/html/index.html
```

## Contribution Workflow

1. **Fork the repository** on GitHub
2. **Create a feature branch** from `main`
```bash
git checkout -b feature/your-feature-name
```

3. **Make your changes** following our code standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Run the full test suite**
```bash
uv run pytest
uv run ruff check .
uv run mypy allocator/
```

7. **Commit with clear messages**
```bash
git commit -m "Add clustering algorithm validation

- Add parameter validation for n_clusters
- Add tests for edge cases
- Update documentation examples"
```

8. **Push and create a Pull Request**

## Code Style Guidelines

### Python Code
- Follow PEP 8 style guidelines
- Use type hints for all function signatures  
- Write docstrings in Google/NumPy style
- Maximum line length: 100 characters
- Use meaningful variable and function names

### Example Function
```python
def cluster_locations(
    data: pd.DataFrame,
    n_clusters: int,
    distance: str = "haversine",
    random_state: Optional[int] = None,
) -> ClusterResult:
    """Cluster geographic locations into balanced groups.
    
    Args:
        data: DataFrame with longitude/latitude columns
        n_clusters: Number of clusters to create
        distance: Distance calculation method
        random_state: Random seed for reproducible results
        
    Returns:
        ClusterResult object with cluster assignments and metadata
        
    Raises:
        ValueError: If n_clusters is invalid
        KeyError: If required columns are missing
    """
```

### Documentation
- Write clear, concise documentation
- Include practical examples for all public functions  
- Update relevant guides when adding features
- Use markdown for all new documentation

## Testing Guidelines

### Test Structure
```
tests/
├── api/              # API function tests
├── core/             # Core algorithm tests  
├── distances/        # Distance calculation tests
├── integration/      # End-to-end tests
└── benchmarks/       # Performance tests
```

### Writing Tests
```python
import pytest
import pandas as pd
from allocator import cluster

def test_cluster_basic():
    """Test basic clustering functionality."""
    data = pd.DataFrame({
        'longitude': [100.5, 100.6, 100.7],
        'latitude': [13.7, 13.8, 13.9],
    })
    
    result = cluster(data, n_clusters=2)
    
    assert result['n_clusters'] == 2
    assert 'cluster' in result['data'].columns
    assert len(result['data']) == 3
    assert set(result['data']['cluster']) == {0, 1}

def test_cluster_invalid_input():
    """Test error handling for invalid input."""
    data = pd.DataFrame({'invalid': [1, 2, 3]})
    
    with pytest.raises(KeyError, match="longitude"):
        cluster(data, n_clusters=2)
```

## Documentation Guidelines

### API Documentation
- All public functions must have complete docstrings
- Include parameter types, return values, and examples
- Document error conditions and edge cases

### Examples
- Provide realistic, practical examples
- Use real-world data when possible  
- Include expected output
- Show both basic and advanced usage

### Guides
- Write step-by-step tutorials for complex workflows
- Include troubleshooting sections
- Link related concepts and functions

## Release Process

### Version Numbering
We follow semantic versioning (SemVer):
- **Major** (1.0.0): Breaking changes
- **Minor** (1.1.0): New features, backward compatible
- **Patch** (1.0.1): Bug fixes, backward compatible

### Preparing a Release
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with release notes
3. Ensure all tests pass and documentation is current
4. Create release PR for review
5. Tag release after merge: `git tag v1.1.0`
6. Release to PyPI is automated via GitHub Actions

## Getting Help

- **Questions**: [GitHub Discussions](https://github.com/geosensing/allocator/discussions)
- **Issues**: [GitHub Issues](https://github.com/geosensing/allocator/issues)  
- **Documentation**: [docs.allocator.ai](https://geosensing.github.io/allocator/)
- **Examples**: See `examples/` directory

## Areas for Contribution

We welcome contributions in these areas:

### Core Features
- New clustering algorithms
- Additional routing methods
- Performance optimizations
- Better error handling

### Documentation
- More real-world examples
- Tutorial improvements  
- API documentation enhancements
- Translation support

### Testing
- Edge case coverage
- Performance benchmarks
- Integration tests
- Property-based testing

### Tooling
- CLI improvements
- Visualization enhancements
- IDE integrations
- CI/CD optimizations

Thank you for contributing to make allocator better for everyone!