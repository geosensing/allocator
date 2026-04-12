#!/usr/bin/env python3
"""
Interactive Visualization Demo

This script demonstrates the new interactive visualization capabilities using folium
for geographic context and polyline decoding for route visualization.

Features:
- Interactive clustering maps with geographic context
- Interactive route maps with proper polyline support
- Comparison between static and interactive visualization
- HTML output for web sharing
"""

from pathlib import Path

import numpy as np

from allocator.api import cluster, route
from allocator.viz import plot_clusters, plot_clusters_interactive, plot_route_interactive


def generate_sample_data():
    """Generate sample geographic data for demonstration."""
    # Sample locations around major US cities
    cities = {
        "New York": [
            [-74.0059, 40.7128],  # NYC
            [-74.0365, 40.7061],  # Jersey City
            [-73.9442, 40.6782],  # Brooklyn
            [-73.8648, 40.7282],  # Queens
            [-73.9973, 40.7505],  # Midtown
        ],
        "San Francisco": [
            [-122.4194, 37.7749],  # SF Downtown
            [-122.4586, 37.7516],  # Mission
            [-122.4376, 37.7849],  # Chinatown
            [-122.4014, 37.7849],  # Financial
            [-122.3959, 37.7849],  # SOMA
        ],
        "Chicago": [
            [-87.6298, 41.8781],  # Downtown
            [-87.6244, 41.8781],  # Loop
            [-87.6298, 41.8919],  # Lincoln Park
            [-87.6244, 41.8588],  # Chinatown
            [-87.6064, 41.8781],  # Lake Shore
        ],
    }

    return cities


def demo_clustering_visualization():
    """Demonstrate interactive clustering visualization."""
    print("🗺️  Interactive Clustering Visualization Demo")
    print("=" * 50)

    cities = generate_sample_data()

    for city_name, coordinates in cities.items():
        print(f"\n📍 Processing {city_name}...")

        # Convert to numpy array
        data = np.array(coordinates)

        # Perform clustering
        print("  🔄 Running K-means clustering...")
        result = cluster(data, n_clusters=2, method="kmeans", distance="haversine", random_state=42)

        # Create output directory
        output_dir = Path("examples/outputs/interactive_demo")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Static visualization (existing)
        print("  📊 Generating static visualization...")
        plot_clusters(
            result.data[["longitude", "latitude"]].values,
            result.labels,
            result.centroids,
            title=f"{city_name} Clustering (Static)",
            save_path=str(output_dir / f"{city_name.lower()}_clustering_static.png"),
            show=False,
        )

        # Interactive visualization (new!)
        print("  🌐 Generating interactive map...")
        plot_clusters_interactive(
            result.data[["longitude", "latitude"]].values,
            result.labels,
            result.centroids,
            title=f"{city_name} Clustering Results",
            save_path=str(output_dir / f"{city_name.lower()}_clustering_interactive.html"),
        )

        print(f"  ✅ Saved: {city_name.lower()}_clustering_interactive.html")
        print(f"     📊 Static chart: {city_name.lower()}_clustering_static.png")


def demo_route_visualization():
    """Demonstrate interactive route visualization."""
    print("\n🛣️  Interactive Route Visualization Demo")
    print("=" * 50)

    cities = generate_sample_data()

    for city_name, coordinates in cities.items():
        print(f"\n📍 Processing {city_name} route...")

        # Convert to numpy array
        data = np.array(coordinates)

        # Generate TSP route
        print("  🔄 Solving TSP...")
        route_result = route(data, method="ortools", distance="haversine")

        # Create output directory
        output_dir = Path("examples/outputs/interactive_demo")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Interactive route visualization
        print("  🌐 Generating interactive route map...")
        plot_route_interactive(
            route_result.data[["longitude", "latitude"]].values,
            route_result.route,
            title=f"{city_name} Optimized Route",
            save_path=str(output_dir / f"{city_name.lower()}_route_interactive.html"),
        )

        print(f"  ✅ Saved: {city_name.lower()}_route_interactive.html")
        print(f"     📏 Total distance: {route_result.total_distance:.2f}")


def create_demo_index():
    """Create an HTML index page linking to all interactive visualizations."""
    output_dir = Path("examples/outputs/interactive_demo")

    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Allocator Interactive Visualization Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .section { margin-bottom: 30px; }
        .city-group { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .links a { margin-right: 15px; text-decoration: none; color: #0066cc; }
        .links a:hover { text-decoration: underline; }
        .description { color: #666; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🗺️ Allocator Interactive Visualization Demo</h1>
        <p class="description">
            Interactive geographic visualizations powered by Folium and Polyline.
            <br>Click links below to explore interactive maps with geographic context.
        </p>
    </div>

    <div class="section">
        <h2>📍 Interactive Clustering Results</h2>
        <p>K-means clustering with geographic map context and interactive exploration.</p>

        <div class="city-group">
            <h3>New York</h3>
            <div class="links">
                <a href="new_york_clustering_interactive.html" target="_blank">🌐 Interactive Map</a>
                <a href="new_york_clustering_static.png" target="_blank">📊 Static Chart</a>
            </div>
        </div>

        <div class="city-group">
            <h3>San Francisco</h3>
            <div class="links">
                <a href="san_francisco_clustering_interactive.html" target="_blank">🌐 Interactive Map</a>
                <a href="san_francisco_clustering_static.png" target="_blank">📊 Static Chart</a>
            </div>
        </div>

        <div class="city-group">
            <h3>Chicago</h3>
            <div class="links">
                <a href="chicago_clustering_interactive.html" target="_blank">🌐 Interactive Map</a>
                <a href="chicago_clustering_static.png" target="_blank">📊 Static Chart</a>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>🛣️ Interactive Route Optimization</h2>
        <p>TSP route optimization with interactive maps and distance calculations.</p>

        <div class="city-group">
            <h3>New York</h3>
            <div class="links">
                <a href="new_york_route_interactive.html" target="_blank">🌐 Interactive Route Map</a>
            </div>
        </div>

        <div class="city-group">
            <h3>San Francisco</h3>
            <div class="links">
                <a href="san_francisco_route_interactive.html" target="_blank">🌐 Interactive Route Map</a>
            </div>
        </div>

        <div class="city-group">
            <h3>Chicago</h3>
            <div class="links">
                <a href="chicago_route_interactive.html" target="_blank">🌐 Interactive Route Map</a>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>🚀 Features Demonstrated</h2>
        <ul>
            <li><strong>Geographic Context:</strong> Real map tiles instead of coordinate plots</li>
            <li><strong>Interactive Exploration:</strong> Zoom, pan, and click for details</li>
            <li><strong>Professional Output:</strong> Shareable HTML maps for presentations</li>
            <li><strong>Hybrid Approach:</strong> Both static analysis charts AND interactive maps</li>
            <li><strong>Distance Calculations:</strong> Haversine distance with visual routes</li>
        </ul>
    </div>
</body>
</html>
    """

    index_path = output_dir / "index.html"
    with open(index_path, "w") as f:
        f.write(html_content)

    print(f"\n📄 Created demo index: {index_path}")
    print("   Open in browser to explore all interactive visualizations!")


def main():
    """Run the complete interactive visualization demo."""
    print("🌟 Allocator Interactive Visualization Demo")
    print("=" * 60)
    print("This demo showcases the new interactive visualization capabilities:")
    print("- Interactive clustering maps with folium")
    print("- Interactive route maps with polyline support")
    print("- Geographic context for better spatial understanding")
    print("=" * 60)

    # Run clustering demo
    demo_clustering_visualization()

    # Run route demo
    demo_route_visualization()

    # Create index page
    create_demo_index()

    print("\n✨ Demo Complete!")
    print("\nFiles generated:")
    print("   📁 examples/outputs/interactive_demo/")
    print("   ├── index.html                          # Main demo page")
    print("   ├── *_clustering_interactive.html       # Interactive cluster maps")
    print("   ├── *_clustering_static.png            # Static cluster charts")
    print("   └── *_route_interactive.html           # Interactive route maps")
    print("\n🌐 Open examples/outputs/interactive_demo/index.html in your browser!")


if __name__ == "__main__":
    main()
