#!/usr/bin/env python3
"""
Generate installation documentation from pyproject.toml.

This script reads the project dependencies and optional-dependencies from pyproject.toml
and generates a comprehensive installation guide.
"""

import tomllib
from pathlib import Path
import sys

def get_dep_description(dep_name: str) -> str:
    """Get human-readable description for a dependency."""
    descriptions = {
        # Core data processing
        'pandas': 'Data manipulation and analysis',
        'numpy': 'Numerical computations',
        'scikit-learn': 'Machine learning algorithms',
        
        # Distance calculations
        'utm': 'Coordinate system transformations',
        'haversine': 'Geographic distance calculations',
        
        # Graph operations
        'networkx': 'Graph algorithms',
        
        # CLI interface
        'click': 'Command-line interface framework',
        'rich': 'Rich terminal output and formatting',
        
        # HTTP requests
        'requests': 'HTTP library for API calls',
        
        # External APIs
        'googlemaps': 'Google Maps API integration',
        
        # Optimization
        'ortools': 'High-performance optimization algorithms',
        
        # Visualization
        'matplotlib': 'Basic plotting and visualization',
        'seaborn': 'Statistical data visualization',
        
        # Algorithm extensions
        'scipy': 'Enhanced mathematical algorithms',
        'Christofides': 'Christofides TSP algorithm for optimal routing',
        
        # Geographic features
        'folium': 'Interactive maps and visualizations',
        'polyline': 'Route encoding for mapping APIs',
        
        # Development tools
        'ruff': 'Modern linting and formatting',
        'mypy': 'Type checking',
        'black': 'Code formatting',
        'isort': 'Import sorting',
        'pre-commit': 'Git hooks for code quality',
        
        # Testing
        'pytest': 'Testing framework',
        'pytest-cov': 'Coverage reporting',
        'pytest-xdist': 'Parallel testing',
        'coverage': 'Code coverage analysis',
        'hypothesis': 'Property-based testing',
        
        # Documentation
        'sphinx': 'Documentation generator',
        'sphinx-rtd-theme': 'Read the Docs theme',
        'myst-parser': 'Markdown support for Sphinx',
        'sphinx-autodoc-typehints': 'Type hints in API docs',
    }
    return descriptions.get(dep_name, 'Additional functionality')

def format_dependency(dep: str) -> tuple[str, str]:
    """Extract package name and version from dependency string."""
    if '>=' in dep:
        name, version = dep.split('>=', 1)
        return name, f"≥{version}"
    elif '>' in dep:
        name, version = dep.split('>', 1)
        return name, f">{version}"
    elif '==' in dep:
        name, version = dep.split('==', 1)
        return name, f"={version}"
    else:
        return dep, ""

def generate_installation_content(project_data: dict) -> str:
    """Generate installation documentation content."""
    
    name = project_data['name']
    requires_python = project_data.get('requires-python', '>=3.11')  # Fix key name
    dependencies = project_data['dependencies']
    optional_deps = project_data.get('optional-dependencies', {})
    
    content = f'''# Installation Guide

## Requirements

**Python Version**: {requires_python}  
**Operating System**: Windows, macOS, Linux

## Basic Installation

### Install from PyPI (Recommended)

```bash
pip install {name}
```

This installs the core {name} package with all essential dependencies for clustering, routing, and assignment operations.

### Install with UV (Fastest)

```bash
uv add {name}
```

UV is a modern, fast Python package manager. If you don't have UV installed:

```bash
pip install uv
uv add {name}
```

## Optional Dependencies

{name} supports several optional dependency groups for extended functionality:

'''

    # Generate optional dependency sections
    for group, deps in optional_deps.items():
        if group in ['all', 'complete']:  # Skip meta-groups
            continue
            
        group_title = group.replace('_', ' ').title()
        content += f'''### {group_title}

```bash
# {get_group_description(group)}
pip install "{name}[{group}]"
```

Includes:
'''
        for dep in deps:
            dep_name, version = format_dependency(dep)
            description = get_dep_description(dep_name)
            version_info = f" {version}" if version else ""
            content += f'- `{dep_name}`{version_info} - {description}\n'
        
        content += '\n'

    # Add convenience groups
    content += f'''## Complete Installation

### All Features

```bash
# Install with all optional features
pip install "{name}[all]"
```

### Complete Development Setup

```bash
# Install everything for development
pip install "{name}[complete]"
```

## Installation Verification

### Quick Test

```python
import {name}
print(f"{name.title()} version: {{{name}.__version__}}")

# Test basic functionality
import pandas as pd

# Create sample data
data = pd.DataFrame({{
    'longitude': [100.5, 100.6, 100.7],
    'latitude': [13.7, 13.8, 13.9]
}})

# Test clustering
result = {name}.cluster(data, n_clusters=2)
print(f"✓ Clustering: Created {{result['n_clusters']}} clusters")

# Test routing  
route = {name}.shortest_path(data)
print(f"✓ Routing: {{route['total_distance']:.1f}}km route")

print("🎉 Installation successful!")
```

### Command Line Interface

```bash
# Test CLI installation
{name} --version

# Test clustering command
echo "longitude,latitude
100.5,13.7
100.6,13.8
100.7,13.9" > test_data.csv

{name} cluster kmeans test_data.csv --n-clusters 2
```

## Troubleshooting

### Common Issues

#### Permission Error on macOS/Linux

```bash
# Use --user flag to install in user directory
pip install --user {name}
```

#### Package Conflicts

```bash
# Create a virtual environment (recommended)
python -m venv {name}_env
source {name}_env/bin/activate  # On Windows: {name}_env\\Scripts\\activate
pip install {name}
```

#### UV Installation Issues

```bash
# Install UV using pip if direct install fails
pip install uv
uv add {name}
```

### Core Dependencies

{name} requires these core packages:

'''

    # List core dependencies
    for dep in dependencies:
        dep_name, version = format_dependency(dep)
        description = get_dep_description(dep_name)
        version_info = f" {version}" if version else ""
        content += f'- **{dep_name}{version_info}** - {description}\n'

    content += f'''
### System Requirements

**Memory**: 2GB+ recommended for large datasets (1000+ points)  
**Storage**: 100MB for package + 50MB per analysis run  
**Network**: Optional for OSRM/Google Maps API features

## Development Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/geosensing/{name}.git
cd {name}

# Install in development mode
pip install -e ".[complete]"

# Set up pre-commit hooks
pre-commit install
```

### Using UV

```bash
# Clone and install with UV
git clone https://github.com/geosensing/{name}.git
cd {name}
uv sync --all-extras
```

## Docker Installation

### Quick Start with Docker

```bash
# Run {name} in Docker container
docker run --rm -v $(pwd):/data python:3.11 bash -c "
    pip install {name} &&
    cd /data &&
    {name} --help
"
```

### Custom Dockerfile

```dockerfile
FROM python:3.11-slim

# Install {name} with all features
RUN pip install {name}[all]

# Set working directory
WORKDIR /workspace

# Default command
CMD ["{name}", "--help"]
```

Build and run:

```bash
docker build -t {name} .
docker run --rm -v $(pwd):/workspace {name}
```

## Next Steps

- 📖 **Quick Start**: [Quickstart Tutorial](quickstart.md)
- 🔧 **API Reference**: [API Documentation](api/clustering.md)
- 💡 **Examples**: [Example Workflows](examples/overview.md)
- 🚀 **CLI Guide**: [Command Line Interface](cli.md)

## Getting Help

- **Documentation**: [https://geosensing.github.io/{name}/](https://geosensing.github.io/{name}/)
- **Issues**: [GitHub Issues](https://github.com/geosensing/{name}/issues)
- **Source**: [GitHub Repository](https://github.com/geosensing/{name})
- **PyPI**: [Package Page](https://pypi.org/project/{name}/)'''

    return content

def get_group_description(group: str) -> str:
    """Get description for an optional dependency group."""
    descriptions = {
        'algorithms': 'Enhanced algorithms including Christofides TSP',
        'geo': 'Interactive mapping and route visualization', 
        'dev': 'Development and testing tools',
        'test': 'Testing framework and coverage tools',
        'docs': 'Documentation building tools',
    }
    return descriptions.get(group, f'{group.title()} features')

def main():
    """Main function to generate installation documentation."""
    try:
        # Read pyproject.toml
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        if not pyproject_path.exists():
            print(f"Error: pyproject.toml not found at {pyproject_path}")
            sys.exit(1)
            
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        
        project_data = data.get("project", {})
        if not project_data:
            print("Error: No [project] section found in pyproject.toml")
            sys.exit(1)
        
        # Generate content
        content = generate_installation_content(project_data)
        
        # Write to docs
        docs_path = Path(__file__).parent.parent / "docs/source/installation.md"
        docs_path.parent.mkdir(parents=True, exist_ok=True)
        docs_path.write_text(content)
        
        print(f"✅ Generated installation docs: {docs_path}")
        print(f"📦 Package: {project_data['name']}")
        print(f"🐍 Python: {project_data.get('requires-python', '>=3.11')}")
        print(f"📋 Core dependencies: {len(project_data['dependencies'])}")
        print(f"🔧 Optional groups: {len(project_data.get('optional-dependencies', {}))}")
        
    except Exception as e:
        print(f"Error generating installation docs: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()