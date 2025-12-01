#!/usr/bin/env python3
"""
Real-World Workflow: Complete allocator demonstration using actual road network data.

This script demonstrates the end-to-end workflow using real OpenStreetMap data
from Delhi, India and Chonburi, Thailand road networks.
"""

import pandas as pd
import numpy as np
import time
from pathlib import Path

import allocator

def load_road_data(city_name: str) -> pd.DataFrame:
    """Load and preprocess road network data for a city."""
    
    file_path = f"examples/inputs/{city_name.lower()}-roads-1k.csv"
    
    print(f"📊 Loading {city_name} road network data...")
    roads = pd.read_csv(file_path)
    
    # Convert road segments to analysis points (using start coordinates)
    points = pd.DataFrame({
        'longitude': roads['start_long'],
        'latitude': roads['start_lat'], 
        'segment_id': roads['segment_id'],
        'road_name': roads['osm_name'].fillna('Unnamed Road'),
        'road_type': roads['osm_type']
    })
    
    # Data quality summary
    unique_roads = roads['osm_name'].nunique()
    road_types = roads['osm_type'].value_counts()
    bounds = {
        'lon_min': points['longitude'].min(),
        'lon_max': points['longitude'].max(), 
        'lat_min': points['latitude'].min(),
        'lat_max': points['latitude'].max()
    }
    
    print(f"✓ Loaded {len(roads):,} road segments")
    print(f"  • {unique_roads} unique road names")
    print(f"  • Road types: {dict(road_types)}")
    print(f"  • Geographic bounds: {bounds['lon_min']:.3f} to {bounds['lon_max']:.3f} lng, {bounds['lat_min']:.3f} to {bounds['lat_max']:.3f} lat")
    
    return points

def clustering_analysis(points: pd.DataFrame, city_name: str, n_clusters: int = 5) -> dict:
    """Perform clustering analysis with multiple methods."""
    
    print(f"\n🎯 Clustering Analysis: {city_name}")
    print("=" * 50)
    
    results = {}
    
    # Use smaller sample for demonstration (full dataset would be slow)
    sample_size = min(200, len(points))
    sample_points = points.sample(n=sample_size, random_state=42).copy()
    
    print(f"Using sample of {sample_size} points for clustering analysis")
    
    # K-means clustering with different distance methods
    methods = ['euclidean', 'haversine']
    
    for method in methods:
        print(f"\n📍 K-means clustering with {method} distance...")
        start_time = time.time()
        
        try:
            cluster_result = allocator.cluster(
                sample_points, 
                n_clusters=n_clusters, 
                distance=method, 
                random_state=42
            )
            
            elapsed = time.time() - start_time
            
            # Analyze clustering quality
            cluster_sizes = cluster_result.data['cluster'].value_counts().sort_index()
            
            print(f"  ✓ Completed in {elapsed:.2f}s")
            print(f"  • Cluster sizes: {dict(cluster_sizes)}")
            print(f"  • Converged: {cluster_result.metadata.get('converged', 'N/A')}")
            print(f"  • Iterations: {cluster_result.metadata.get('iterations', 'N/A')}")
            
            # Calculate average intra-cluster distances
            avg_distances = []
            for cluster_id in range(n_clusters):
                cluster_points = cluster_result.data[cluster_result.data['cluster'] == cluster_id]
                if len(cluster_points) > 1:
                    coords = cluster_points[['longitude', 'latitude']].values
                    distances = allocator.get_distance_matrix(coords, method=method)
                    avg_dist = np.mean(distances[np.triu_indices_from(distances, k=1)])
                    avg_distances.append(avg_dist)
            
            if avg_distances:
                overall_avg = np.mean(avg_distances) / 1000  # Convert to km
                print(f"  • Average intra-cluster distance: {overall_avg:.2f} km")
            
            results[method] = {
                'result': cluster_result,
                'elapsed_time': elapsed,
                'cluster_sizes': dict(cluster_sizes),
                'avg_intra_cluster_distance': overall_avg if avg_distances else None
            }
            
        except Exception as e:
            print(f"  ✗ Error with {method}: {e}")
            results[method] = {'error': str(e)}
    
    return results

def routing_analysis(points: pd.DataFrame, city_name: str) -> dict:
    """Perform TSP routing analysis."""
    
    print(f"\n🛣️ Route Optimization Analysis: {city_name}")
    print("=" * 50)
    
    # Use smaller subset for TSP (TSP is computationally intensive)
    route_points = points.sample(n=min(15, len(points)), random_state=42).copy()
    
    print(f"Finding optimal route through {len(route_points)} key locations...")
    
    try:
        start_time = time.time()
        route_result = allocator.shortest_path(route_points, method='ortools')
        elapsed = time.time() - start_time
        
        print(f"✓ Route optimization completed in {elapsed:.2f}s")
        print(f"  • Total route distance: {route_result.total_distance/1000:.2f} km")
        print(f"  • Average distance between stops: {route_result.total_distance/len(route_points)/1000:.2f} km")
        
        # Show route order with road names
        print(f"\n📋 Optimal route order:")
        route_order = route_result.data.sort_values('route_order')
        for i, (_, stop) in enumerate(route_order.iterrows()):
            road_name = stop['road_name']
            if len(road_name) > 40:
                road_name = road_name[:37] + "..."
            print(f"    {int(stop['route_order'])}: {road_name} ({stop['road_type']})")
        
        return {
            'result': route_result,
            'elapsed_time': elapsed,
            'total_distance_km': route_result.total_distance/1000,
            'avg_distance_km': route_result.total_distance/len(route_points)/1000
        }
        
    except Exception as e:
        print(f"✗ Route optimization error: {e}")
        return {'error': str(e)}

def assignment_analysis(points: pd.DataFrame, city_name: str) -> dict:
    """Perform assignment optimization analysis."""
    
    print(f"\n📍 Assignment Optimization Analysis: {city_name}")
    print("=" * 50)
    
    # Create service depot locations based on geographic distribution
    bounds = {
        'lon_min': points['longitude'].min(),
        'lon_max': points['longitude'].max(),
        'lat_min': points['latitude'].min(), 
        'lat_max': points['latitude'].max()
    }
    
    # Strategic depot placement
    depots = pd.DataFrame({
        'longitude': [
            bounds['lon_min'] + 0.3 * (bounds['lon_max'] - bounds['lon_min']),
            bounds['lon_min'] + 0.7 * (bounds['lon_max'] - bounds['lon_min']),
            (bounds['lon_min'] + bounds['lon_max']) / 2
        ],
        'latitude': [
            bounds['lat_min'] + 0.3 * (bounds['lat_max'] - bounds['lat_min']),
            bounds['lat_min'] + 0.7 * (bounds['lat_max'] - bounds['lat_min']),
            (bounds['lat_min'] + bounds['lat_max']) / 2
        ],
        'depot_name': [f'{city_name}_South', f'{city_name}_North', f'{city_name}_Central'],
        'capacity': [300, 300, 400]
    })
    
    print(f"Service depot locations:")
    for _, depot in depots.iterrows():
        print(f"  • {depot['depot_name']}: ({depot['longitude']:.3f}, {depot['latitude']:.3f}) - Capacity: {depot['capacity']}")
    
    # Sample points for assignment analysis
    sample_points = points.sample(n=min(100, len(points)), random_state=42).copy()
    
    try:
        start_time = time.time()
        assignment_result = allocator.assign_to_closest(sample_points, depots, distance='haversine')
        elapsed = time.time() - start_time
        
        print(f"\n✓ Assignment optimization completed in {elapsed:.2f}s")
        
        # Analyze assignments
        assignments = assignment_result.data.groupby('assigned_worker').size()
        print(f"  • Assignment distribution:")
        for depot_id, count in assignments.items():
            depot_name = depots.iloc[int(depot_id)]['depot_name']
            capacity = depots.iloc[int(depot_id)]['capacity']
            utilization = (count / capacity) * 100
            print(f"    {depot_name}: {count} locations ({utilization:.1f}% capacity)")
        
        # Calculate assignment distances
        avg_distances = []
        for depot_id in assignments.index:
            assigned_points = assignment_result.data[assignment_result.data['assigned_worker'] == depot_id]
            depot_loc = depots.iloc[int(depot_id)]
            
            for _, point in assigned_points.iterrows():
                point_coords = np.array([[point['longitude'], point['latitude']]])
                depot_coords = np.array([[depot_loc['longitude'], depot_loc['latitude']]])
                distance = allocator.get_distance_matrix(point_coords, depot_coords, method='haversine')[0, 0]
                avg_distances.append(distance)
        
        if avg_distances:
            overall_avg_distance = np.mean(avg_distances) / 1000
            print(f"  • Average assignment distance: {overall_avg_distance:.2f} km")
        
        return {
            'result': assignment_result,
            'elapsed_time': elapsed,
            'assignments': dict(assignments),
            'avg_assignment_distance_km': overall_avg_distance if avg_distances else None,
            'depot_utilization': {depots.iloc[i]['depot_name']: (assignments.get(i, 0) / depots.iloc[i]['capacity']) * 100 for i in range(len(depots))}
        }
        
    except Exception as e:
        print(f"✗ Assignment optimization error: {e}")
        return {'error': str(e)}

def distance_matrix_analysis(points: pd.DataFrame, city_name: str) -> dict:
    """Analyze different distance calculation methods."""
    
    print(f"\n📐 Distance Matrix Analysis: {city_name}")
    print("=" * 50)
    
    # Select key intersections for comparison
    major_roads = points[points['road_type'].isin(['primary', 'trunk'])].head(10)
    
    if len(major_roads) < 2:
        major_roads = points.head(10)
    
    print(f"Comparing distance methods using {len(major_roads)} key locations...")
    
    coords = major_roads[['longitude', 'latitude']].values
    methods = ['euclidean', 'haversine']
    results = {}
    
    for method in methods:
        try:
            start_time = time.time()
            distances = allocator.get_distance_matrix(coords, method=method)
            elapsed = time.time() - start_time
            
            # Calculate statistics
            upper_triangle = distances[np.triu_indices_from(distances, k=1)]
            stats = {
                'mean_distance_km': np.mean(upper_triangle) / 1000,
                'max_distance_km': np.max(upper_triangle) / 1000,
                'min_distance_km': np.min(upper_triangle) / 1000,
                'std_distance_km': np.std(upper_triangle) / 1000
            }
            
            print(f"\n📊 {method.capitalize()} distance statistics:")
            print(f"  • Mean distance: {stats['mean_distance_km']:.2f} km")
            print(f"  • Max distance: {stats['max_distance_km']:.2f} km") 
            print(f"  • Min distance: {stats['min_distance_km']:.2f} km")
            print(f"  • Std deviation: {stats['std_distance_km']:.2f} km")
            print(f"  • Calculation time: {elapsed:.4f}s")
            
            results[method] = {
                'distances': distances,
                'statistics': stats,
                'elapsed_time': elapsed
            }
            
        except Exception as e:
            print(f"✗ Error with {method}: {e}")
            results[method] = {'error': str(e)}
    
    return results

def main():
    """Run complete real-world workflow demonstration."""
    
    print("🌏 Real-World Allocator Workflow Demonstration")
    print("=" * 60)
    print("Using actual OpenStreetMap road network data")
    print(f"Allocator version: {allocator.__version__}")
    
    # Available datasets
    cities = ['Delhi', 'Chonburi']
    all_results = {}
    
    for city in cities:
        print(f"\n{'='*60}")
        print(f"🏙️ ANALYZING {city.upper()} ROAD NETWORK")
        print(f"{'='*60}")
        
        try:
            # Load and preprocess data
            points = load_road_data(city)
            
            # Run all analyses
            city_results = {
                'data_info': {
                    'total_segments': len(points),
                    'geographic_bounds': {
                        'longitude': [points['longitude'].min(), points['longitude'].max()],
                        'latitude': [points['latitude'].min(), points['latitude'].max()]
                    },
                    'road_types': points['road_type'].value_counts().to_dict()
                },
                'clustering': clustering_analysis(points, city),
                'routing': routing_analysis(points, city),
                'assignment': assignment_analysis(points, city),
                'distance_methods': distance_matrix_analysis(points, city)
            }
            
            all_results[city] = city_results
            
        except Exception as e:
            print(f"✗ Error processing {city}: {e}")
            all_results[city] = {'error': str(e)}
    
    # Final summary
    print(f"\n{'='*60}")
    print("📈 WORKFLOW SUMMARY")
    print(f"{'='*60}")
    
    for city, results in all_results.items():
        if 'error' in results:
            print(f"\n{city}: Processing failed - {results['error']}")
            continue
            
        print(f"\n🏙️ {city} Results Summary:")
        print(f"  • Dataset: {results['data_info']['total_segments']:,} road segments")
        
        # Clustering summary
        clustering = results.get('clustering', {})
        if 'euclidean' in clustering and 'result' in clustering['euclidean']:
            clusters = len(clustering['euclidean']['result'].data['cluster'].unique())
            time_taken = clustering['euclidean']['elapsed_time']
            print(f"  • Clustering: {clusters} zones in {time_taken:.2f}s")
        
        # Routing summary  
        routing = results.get('routing', {})
        if 'result' in routing:
            route_distance = routing['total_distance_km']
            route_time = routing['elapsed_time']
            print(f"  • Route optimization: {route_distance:.1f}km route in {route_time:.2f}s")
        
        # Assignment summary
        assignment = results.get('assignment', {})
        if 'result' in assignment:
            assign_time = assignment['elapsed_time']
            avg_distance = assignment.get('avg_assignment_distance_km', 0)
            print(f"  • Assignment: Avg {avg_distance:.1f}km distance in {assign_time:.2f}s")
    
    print(f"\n🎯 Business Applications Demonstrated:")
    print(f"  • Urban planning: Road network analysis and zone creation")
    print(f"  • Logistics: Delivery route optimization and depot placement")
    print(f"  • Emergency services: Response zone assignments")
    print(f"  • Maintenance: Infrastructure inspection scheduling")
    print(f"  • Transportation: Public transit route planning")
    
    print(f"\n✨ Key Features Showcased:")
    print(f"  • Real geographic data processing")
    print(f"  • Multiple clustering algorithms")
    print(f"  • TSP route optimization")  
    print(f"  • Distance-based assignments")
    print(f"  • Multiple distance calculation methods")
    print(f"  • Performance metrics and timing")
    
    print(f"\n🎉 Real-world workflow demonstration complete!")
    print(f"   Production-ready results using actual OpenStreetMap data")
    print(f"   from {len(cities)} major urban areas.")


if __name__ == "__main__":
    main()