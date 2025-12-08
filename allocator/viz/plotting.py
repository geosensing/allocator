"""
Visualization utilities for allocator package.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors

try:
    import folium
    from folium import plugins

    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

try:
    import polyline

    HAS_POLYLINE = True
except ImportError:
    HAS_POLYLINE = False


def plot_clusters(
    data: np.ndarray | pd.DataFrame,
    labels: np.ndarray,
    centroids: np.ndarray | None = None,
    title: str = "Clustering Results",
    save_path: str | None = None,
    show: bool = True,
) -> None:
    """
    Plot clustering results.

    Args:
        data: Data points as numpy array [n, 2] with [lon, lat] or DataFrame with longitude, latitude
        labels: Cluster assignments for each point
        centroids: Optional cluster centers as numpy array [k, 2]
        title: Plot title
        save_path: Path to save plot (optional)
        show: Whether to display plot
    """
    # Convert DataFrame to numpy array if needed
    if isinstance(data, pd.DataFrame):
        if "longitude" in data.columns and "latitude" in data.columns:
            X = data[["longitude", "latitude"]].values
        else:
            raise ValueError("DataFrame must contain 'longitude' and 'latitude' columns")
    else:
        X = data

    fig = plt.figure(figsize=(8, 8))
    plt.ticklabel_format(useOffset=False)
    cvalues = list(colors.cnames.values())

    n_clusters = len(np.unique(labels))

    ax = fig.add_subplot(1, 1, 1)
    for k, col in zip(range(n_clusters), cvalues, strict=False):
        my_members = labels == k
        ax.plot(X[my_members, 0], X[my_members, 1], "w", markerfacecolor=col, marker=".")

        if centroids is not None:
            ax.plot(
                centroids[k][0],
                centroids[k][1],
                "o",
                markerfacecolor=col,
                markeredgecolor="k",
                markersize=6,
            )

    ax.set_title(title)
    # ax.set_xticks(())
    # ax.set_yticks(())

    if save_path:
        fig.savefig(save_path)

    if show:
        plt.show()

    plt.close()


def plot_assignments(
    data: pd.DataFrame,
    title: str = "Assignment Results",
    save_path: str | None = None,
    show: bool = True,
) -> None:
    """
    Plot assignment results for sort_by_distance type algorithms.

    Args:
        data: DataFrame with longitude, latitude, and assigned_points columns
        title: Plot title
        save_path: Path to save plot (optional)
        show: Whether to display plot
    """

    if "assigned_points" not in data.columns:
        raise ValueError("DataFrame must contain 'assigned_points' column")

    X = data[["longitude", "latitude"]].values
    labels = data["assigned_points"].values - 1  # Convert to 0-based indexing

    # Use the main cluster plotting function
    plot_clusters(X, labels, centroids=None, title=title, save_path=save_path, show=show)


def plot_route(
    route_points: np.ndarray,
    route_order: list[int] | None = None,
    title: str = "Route",
    save_path: str | None = None,
    show: bool = True,
) -> None:
    """
    Plot TSP/routing results.

    Args:
        route_points: Points in the route as numpy array [n, 2] with [lon, lat]
        route_order: Order to visit points (optional, defaults to sequential)
        title: Plot title
        save_path: Path to save plot (optional)
        show: Whether to display plot
    """
    if route_order is None:
        route_order = list(range(len(route_points)))

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1)

    # Plot points
    ax.scatter(route_points[:, 0], route_points[:, 1], c="red", s=50, zorder=5)

    # Plot route
    ordered_points = route_points[route_order]
    # Add return to start
    route_x = np.append(ordered_points[:, 0], ordered_points[0, 0])
    route_y = np.append(ordered_points[:, 1], ordered_points[0, 1])

    ax.plot(route_x, route_y, "b-", linewidth=2, alpha=0.7)

    # Add point labels
    for i, (x, y) in enumerate(route_points):
        ax.annotate(str(i), (x, y), xytext=(5, 5), textcoords="offset points")

    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, alpha=0.3)

    if save_path:
        fig.savefig(save_path)

    if show:
        plt.show()

    plt.close()


def plot_comparison(
    data1: dict,
    data2: dict,
    labels: list[str] | None = None,
    title: str = "Comparison",
    save_path: str | None = None,
    show: bool = True,
) -> None:
    """
    Plot comparison between two clustering methods.

    Args:
        data1: First dataset with 'points' and 'labels' keys
        data2: Second dataset with 'points' and 'labels' keys
        labels: Labels for the two methods
        title: Plot title
        save_path: Path to save plot (optional)
        show: Whether to display plot
    """
    if labels is None:
        labels = ["Method 1", "Method 2"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Plot first method
    plot_clusters_on_axis(ax1, data1["points"], data1["labels"], title=f"{title} - {labels[0]}")

    # Plot second method
    plot_clusters_on_axis(ax2, data2["points"], data2["labels"], title=f"{title} - {labels[1]}")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path)

    if show:
        plt.show()

    plt.close()


def plot_clusters_on_axis(ax, data: np.ndarray, labels: np.ndarray, title: str = "") -> None:
    """Helper function to plot clusters on a given axis."""
    from matplotlib import colors

    cvalues = list(colors.cnames.values())
    n_clusters = len(np.unique(labels))

    for k, col in zip(range(n_clusters), cvalues, strict=False):
        my_members = labels == k
        ax.plot(data[my_members, 0], data[my_members, 1], "w", markerfacecolor=col, marker=".")

    ax.set_title(title)
    ax.grid(True, alpha=0.3)


def plot_clusters_interactive(
    data: np.ndarray | pd.DataFrame,
    labels: np.ndarray,
    centroids: np.ndarray | None = None,
    title: str = "Interactive Clustering Results",
    save_path: str | None = None,
) -> folium.Map:
    """
    Create an interactive map visualization of clustering results using folium.

    Args:
        data: Data points as numpy array [n, 2] with [lon, lat] or DataFrame with longitude, latitude
        labels: Cluster assignments for each point
        centroids: Optional cluster centers as numpy array [k, 2]
        title: Map title (shown as map title)
        save_path: Path to save HTML file (optional)

    Returns:
        Folium map object that can be displayed in Jupyter or saved to HTML

    Raises:
        ImportError: If folium is not installed
    """
    if not HAS_FOLIUM:
        raise ImportError(
            "folium is required for interactive visualization. "
            "Install it with: pip install 'allocator[geo]'"
        )

    # Convert DataFrame to numpy array if needed
    if isinstance(data, pd.DataFrame):
        if "longitude" in data.columns and "latitude" in data.columns:
            X = data[["longitude", "latitude"]].values
        else:
            raise ValueError("DataFrame must contain 'longitude' and 'latitude' columns")
    else:
        X = data

    # Calculate map center and zoom
    center_lat = X[:, 1].mean()
    center_lon = X[:, 0].mean()

    # Calculate bounds for initial zoom
    lat_range = X[:, 1].max() - X[:, 1].min()
    lon_range = X[:, 0].max() - X[:, 0].min()
    max_range = max(lat_range, lon_range)

    # Estimate appropriate zoom level
    if max_range < 0.01:
        zoom_start = 14
    elif max_range < 0.1:
        zoom_start = 12
    elif max_range < 1.0:
        zoom_start = 10
    else:
        zoom_start = 8

    # Create base map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start, tiles="OpenStreetMap")

    # Color palette for clusters
    n_clusters = len(np.unique(labels))
    color_palette = [
        "#FF6B6B",
        "#4ECDC4",
        "#45B7D1",
        "#96CEB4",
        "#FECA57",
        "#FF9FF3",
        "#54A0FF",
        "#5F27CD",
        "#00D2D3",
        "#FF9F43",
        "#A55EEA",
        "#26DE81",
        "#FD79A8",
        "#FDCB6E",
        "#6C5CE7",
    ]

    # Extend palette if needed
    while len(color_palette) < n_clusters:
        color_palette.extend(color_palette)

    # Add data points to map
    for i, (lon, lat) in enumerate(X):
        cluster_id = labels[i]
        color = color_palette[cluster_id % len(color_palette)]

        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            popup=f"Point {i}<br>Cluster: {cluster_id}<br>Coords: ({lon:.4f}, {lat:.4f})",
            color="white",
            weight=1,
            fillColor=color,
            fillOpacity=0.8,
        ).add_to(m)

    # Add centroids if provided
    if centroids is not None:
        for k, (lon, lat) in enumerate(centroids):
            color = color_palette[k % len(color_palette)]
            folium.Marker(
                location=[lat, lon],
                popup=f"Centroid {k}<br>Coords: ({lon:.4f}, {lat:.4f})",
                icon=folium.Icon(color="black", icon="star", prefix="fa"),
                tooltip=f"Cluster {k} Centroid",
            ).add_to(m)

    # Add legend
    legend_html = f"""
    <div style="position: fixed;
                top: 10px; left: 50px; width: 200px; height: auto;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:14px; padding: 10px">
    <h4>{title}</h4>
    <p><strong>Clusters:</strong> {n_clusters}</p>
    <p><strong>Points:</strong> {len(X)}</p>
    """

    for k in range(min(n_clusters, 8)):  # Show first 8 clusters in legend
        color = color_palette[k]
        legend_html += f'<p><span style="color:{color};">●</span> Cluster {k}</p>'

    if n_clusters > 8:
        legend_html += f"<p>... and {n_clusters - 8} more</p>"

    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add fullscreen button
    plugins.Fullscreen().add_to(m)

    # Save if path provided
    if save_path:
        m.save(save_path)

    return m


def plot_route_interactive(
    route_points: np.ndarray,
    route_order: list[int] | None = None,
    route_geometry: str | None = None,
    title: str = "Interactive Route",
    save_path: str | None = None,
) -> folium.Map:
    """
    Create an interactive map visualization of TSP/routing results using folium.

    Args:
        route_points: Points in the route as numpy array [n, 2] with [lon, lat]
        route_order: Order to visit points (optional, defaults to sequential)
        route_geometry: Optional encoded polyline string from routing API (OSRM/Google)
        title: Map title
        save_path: Path to save HTML file (optional)

    Returns:
        Folium map object that can be displayed in Jupyter or saved to HTML

    Raises:
        ImportError: If folium is not installed
    """
    if not HAS_FOLIUM:
        raise ImportError(
            "folium is required for interactive route visualization. "
            "Install it with: pip install 'allocator[geo]'"
        )

    if route_order is None:
        route_order = list(range(len(route_points)))

    # Calculate map center and bounds
    center_lat = route_points[:, 1].mean()
    center_lon = route_points[:, 0].mean()

    lat_range = route_points[:, 1].max() - route_points[:, 1].min()
    lon_range = route_points[:, 0].max() - route_points[:, 0].min()
    max_range = max(lat_range, lon_range)

    # Estimate zoom level
    if max_range < 0.01:
        zoom_start = 14
    elif max_range < 0.1:
        zoom_start = 12
    elif max_range < 1.0:
        zoom_start = 10
    else:
        zoom_start = 8

    # Create base map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start, tiles="OpenStreetMap")

    # Add route line
    if route_geometry and HAS_POLYLINE:
        # Decode polyline geometry from routing API
        try:
            decoded_coords = polyline.decode(route_geometry)
            # Convert to [lat, lon] format for folium
            route_coords = [[lat, lon] for lat, lon in decoded_coords]

            folium.PolyLine(
                locations=route_coords, color="blue", weight=4, opacity=0.8, popup="Optimized Route"
            ).add_to(m)
        except Exception:
            # Fall back to straight line connections if decoding fails
            _add_straight_line_route(m, route_points, route_order)
    else:
        # Use straight line connections between points
        _add_straight_line_route(m, route_points, route_order)

    # Add route points
    for i, point_idx in enumerate(route_order):
        lon, lat = route_points[point_idx]

        # Color-code start, end, and intermediate points
        if i == 0:
            icon_color = "green"
            icon_symbol = "play"
            label = "Start"
        elif i == len(route_order) - 1:
            icon_color = "red"
            icon_symbol = "stop"
            label = "End"
        else:
            icon_color = "blue"
            icon_symbol = f"{i}"
            label = f"Stop {i}"

        folium.Marker(
            location=[lat, lon],
            popup=f"{label}<br>Point {point_idx}<br>Coords: ({lon:.4f}, {lat:.4f})",
            icon=folium.Icon(color=icon_color, icon=icon_symbol, prefix="fa"),
            tooltip=f"{label} (Point {point_idx})",
        ).add_to(m)

    # Calculate route statistics
    total_distance = _calculate_route_distance(route_points, route_order)

    # Add info panel
    info_html = f"""
    <div style="position: fixed;
                top: 10px; right: 10px; width: 250px; height: auto;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:14px; padding: 10px">
    <h4>{title}</h4>
    <p><strong>Points:</strong> {len(route_points)}</p>
    <p><strong>Route Type:</strong> {"API Route" if route_geometry else "Direct Lines"}</p>
    <p><strong>Est. Distance:</strong> {total_distance:.2f} km</p>
    <hr>
    <p><span style="color:green;">●</span> Start Point</p>
    <p><span style="color:blue;">●</span> Intermediate</p>
    <p><span style="color:red;">●</span> End Point</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(info_html))

    # Add fullscreen button
    plugins.Fullscreen().add_to(m)

    # Save if path provided
    if save_path:
        m.save(save_path)

    return m


def _add_straight_line_route(
    m: folium.Map, route_points: np.ndarray, route_order: list[int]
) -> None:
    """Add straight line connections between route points."""
    ordered_points = route_points[route_order]

    # Create route coordinates including return to start
    route_coords = [[lat, lon] for lon, lat in ordered_points]
    route_coords.append([ordered_points[0][1], ordered_points[0][0]])  # Return to start

    folium.PolyLine(
        locations=route_coords,
        color="blue",
        weight=3,
        opacity=0.7,
        popup="Direct Route (Straight Lines)",
    ).add_to(m)


def _calculate_route_distance(route_points: np.ndarray, route_order: list[int]) -> float:
    """Calculate approximate route distance using haversine formula."""
    from math import asin, cos, radians, sin, sqrt

    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points on Earth using haversine formula."""
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))

        # Earth radius in kilometers
        r = 6371
        return c * r

    total_distance = 0.0
    ordered_points = route_points[route_order]

    # Calculate distances between consecutive points
    for i in range(len(ordered_points)):
        current_point = ordered_points[i]
        next_point = ordered_points[(i + 1) % len(ordered_points)]  # Return to start

        distance = haversine_distance(
            current_point[1],
            current_point[0],  # lat1, lon1
            next_point[1],
            next_point[0],  # lat2, lon2
        )
        total_distance += distance

    return total_distance
