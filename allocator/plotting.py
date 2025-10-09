"""
Visualization utilities for allocator package.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def plot_clusters(data: np.ndarray | pd.DataFrame, labels: np.ndarray, 
                 centroids: np.ndarray | None = None, title: str = "Clustering Results", 
                 save_path: str | None = None, show: bool = True) -> None:
    """
    Plot clustering results.
    
    Args:
        data: Data points as numpy array [n, 2] with [lon, lat] or DataFrame with start_long, start_lat
        labels: Cluster assignments for each point
        centroids: Optional cluster centers as numpy array [k, 2]
        title: Plot title
        save_path: Path to save plot (optional)
        show: Whether to display plot
    """
    import matplotlib.pyplot as plt
    from matplotlib import colors
    
    # Convert DataFrame to numpy array if needed
    if isinstance(data, pd.DataFrame):
        if 'start_long' in data.columns and 'start_lat' in data.columns:
            X = data[['start_long', 'start_lat']].values
        else:
            raise ValueError("DataFrame must contain 'start_long' and 'start_lat' columns")
    else:
        X = data
    
    fig = plt.figure(figsize=(8, 8))
    plt.ticklabel_format(useOffset=False)
    cvalues = list(colors.cnames.values())
    
    n_clusters = len(np.unique(labels))
    
    ax = fig.add_subplot(1, 1, 1)
    for k, col in zip(range(n_clusters), cvalues):
        my_members = labels == k
        ax.plot(X[my_members, 0], X[my_members, 1], 'w',
                markerfacecolor=col, marker='.')
        
        if centroids is not None:
            ax.plot(centroids[k][0], centroids[k][1], 'o',
                    markerfacecolor=col, markeredgecolor='k', markersize=6)
    
    ax.set_title(title)
    # ax.set_xticks(())
    # ax.set_yticks(())
    
    if save_path:
        fig.savefig(save_path)
    
    if show:
        plt.show()
    
    plt.close()


def plot_assignments(data: pd.DataFrame, title: str = "Assignment Results",
                    save_path: str | None = None, show: bool = True) -> None:
    """
    Plot assignment results for sort_by_distance type algorithms.
    
    Args:
        data: DataFrame with start_long, start_lat, and assigned_points columns
        title: Plot title
        save_path: Path to save plot (optional) 
        show: Whether to display plot
    """
    import matplotlib.pyplot as plt
    from matplotlib import colors
    
    if 'assigned_points' not in data.columns:
        raise ValueError("DataFrame must contain 'assigned_points' column")
    
    X = data[['start_long', 'start_lat']].values
    labels = data['assigned_points'].values - 1  # Convert to 0-based indexing
    
    # Use the main cluster plotting function
    plot_clusters(X, labels, centroids=None, title=title, save_path=save_path, show=show)


def plot_route(route_points: np.ndarray, route_order: list[int] | None = None,
               title: str = "Route", save_path: str | None = None, show: bool = True) -> None:
    """
    Plot TSP/routing results.
    
    Args:
        route_points: Points in the route as numpy array [n, 2] with [lon, lat]
        route_order: Order to visit points (optional, defaults to sequential)
        title: Plot title
        save_path: Path to save plot (optional)
        show: Whether to display plot
    """
    import matplotlib.pyplot as plt
    
    if route_order is None:
        route_order = list(range(len(route_points)))
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1)
    
    # Plot points
    ax.scatter(route_points[:, 0], route_points[:, 1], c='red', s=50, zorder=5)
    
    # Plot route
    ordered_points = route_points[route_order]
    # Add return to start
    route_x = np.append(ordered_points[:, 0], ordered_points[0, 0])
    route_y = np.append(ordered_points[:, 1], ordered_points[0, 1])
    
    ax.plot(route_x, route_y, 'b-', linewidth=2, alpha=0.7)
    
    # Add point labels
    for i, (x, y) in enumerate(route_points):
        ax.annotate(str(i), (x, y), xytext=(5, 5), textcoords='offset points')
    
    ax.set_title(title)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.grid(True, alpha=0.3)
    
    if save_path:
        fig.savefig(save_path)
    
    if show:
        plt.show()
    
    plt.close()


def plot_comparison(data1: dict, data2: dict, labels: list[str] = ["Method 1", "Method 2"],
                   title: str = "Comparison", save_path: str | None = None, show: bool = True) -> None:
    """
    Plot comparison between two methods (used by compare_kahip_kmeans).
    
    Args:
        data1: First dataset with 'points' and 'labels' keys
        data2: Second dataset with 'points' and 'labels' keys
        labels: Labels for the two methods
        title: Plot title
        save_path: Path to save plot (optional)
        show: Whether to display plot
    """
    import matplotlib.pyplot as plt
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot first method
    plot_clusters_on_axis(ax1, data1['points'], data1['labels'], 
                         title=f"{title} - {labels[0]}")
    
    # Plot second method  
    plot_clusters_on_axis(ax2, data2['points'], data2['labels'],
                         title=f"{title} - {labels[1]}")
    
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
    
    for k, col in zip(range(n_clusters), cvalues):
        my_members = labels == k
        ax.plot(data[my_members, 0], data[my_members, 1], 'w',
                markerfacecolor=col, marker='.')
    
    ax.set_title(title)
    ax.grid(True, alpha=0.3)