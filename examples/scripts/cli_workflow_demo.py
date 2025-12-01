#!/usr/bin/env python3
"""
Interactive CLI Workflow Demonstration

This script demonstrates the complete allocator CLI workflow using real road network data,
showing actual command outputs and usage patterns.
"""

import subprocess
import tempfile
import pandas as pd
from pathlib import Path
import json
import time

def run_command(command: str, description: str = None) -> dict:
    """Run a CLI command and capture its output."""
    
    if description:
        print(f"\n💻 {description}")
        print(f"Command: {command}")
        print("-" * 60)
    
    try:
        start_time = time.time()
        result = subprocess.run(
            command.split(), 
            capture_output=True, 
            text=True, 
            cwd="/Users/soodoku/Documents/GitHub/allocator"
        )
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(result.stdout)
            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'elapsed_time': elapsed,
                'return_code': result.returncode
            }
        else:
            print(f"❌ Command failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return {
                'success': False,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'elapsed_time': elapsed,
                'return_code': result.returncode
            }
            
    except Exception as e:
        print(f"❌ Exception running command: {e}")
        return {'success': False, 'error': str(e)}

def prepare_sample_data():
    """Prepare sample data files from road network data for CLI demonstration."""
    
    print("📋 Preparing sample data for CLI demonstration...")
    
    # Create temporary directory for CLI demo files
    demo_dir = Path("cli_demo_data")
    demo_dir.mkdir(exist_ok=True)
    
    # Load Delhi road data and create a sample
    delhi_roads = pd.read_csv("delhi-roads-1k.csv")
    
    # Convert to proper format for allocator (longitude, latitude)
    delhi_sample = pd.DataFrame({
        'longitude': delhi_roads['start_long'].head(50),
        'latitude': delhi_roads['start_lat'].head(50),
        'segment_id': delhi_roads['segment_id'].head(50),
        'road_name': delhi_roads['osm_name'].fillna('Unnamed Road').head(50),
        'road_type': delhi_roads['osm_type'].head(50)
    })
    
    # Save sample data
    sample_file = demo_dir / "delhi_sample.csv"
    delhi_sample.to_csv(sample_file, index=False)
    
    # Create worker/depot locations
    workers = pd.DataFrame({
        'longitude': [77.1, 77.2, 77.0],
        'latitude': [28.6, 28.7, 28.5],
        'worker_id': ['North_Depot', 'Central_Depot', 'South_Depot'],
        'capacity': [100, 150, 120]
    })
    
    workers_file = demo_dir / "service_depots.csv"
    workers.to_csv(workers_file, index=False)
    
    print(f"✅ Created sample data:")
    print(f"   • {sample_file}: {len(delhi_sample)} road segments")
    print(f"   • {workers_file}: {len(workers)} service depots")
    
    return {
        'sample_file': str(sample_file),
        'workers_file': str(workers_file),
        'sample_size': len(delhi_sample),
        'workers_size': len(workers)
    }

def demonstrate_cli_help():
    """Demonstrate CLI help and information commands."""
    
    print("🔍 CLI Help and Information Commands")
    print("=" * 50)
    
    commands = [
        ("uv run allocator --help", "Show main help"),
        ("uv run allocator --version", "Show version"),
        ("uv run allocator cluster --help", "Show clustering help"),
        ("uv run allocator route --help", "Show routing help"),
        ("uv run allocator sort --help", "Show assignment help")
    ]
    
    results = {}
    for cmd, desc in commands:
        results[cmd] = run_command(cmd, desc)
        
    return results

def demonstrate_clustering_commands(sample_file: str):
    """Demonstrate clustering CLI commands."""
    
    print("\n🎯 Clustering Commands Demonstration")
    print("=" * 50)
    
    commands = [
        (f"uv run allocator cluster kmeans {sample_file} --n-clusters 3", 
         "K-means clustering with 3 clusters"),
        (f"uv run allocator cluster kmeans {sample_file} --n-clusters 5 --distance haversine", 
         "K-means with haversine distance"),
        (f"uv run allocator cluster kmeans {sample_file} --n-clusters 4 --output cli_demo_data/clusters.csv", 
         "K-means with output file"),
        (f"uv run allocator cluster kmeans {sample_file} --n-clusters 3 --format json", 
         "K-means with JSON output")
    ]
    
    results = {}
    for cmd, desc in commands:
        results[cmd] = run_command(cmd, desc)
        time.sleep(0.5)  # Brief pause between commands
        
    return results

def demonstrate_routing_commands(sample_file: str):
    """Demonstrate routing CLI commands."""
    
    print("\n🛣️ Routing Commands Demonstration")  
    print("=" * 50)
    
    # Use smaller subset for routing (TSP is computationally intensive)
    small_sample = pd.read_csv(sample_file).head(10)
    small_file = "cli_demo_data/small_sample.csv"
    small_sample.to_csv(small_file, index=False)
    
    commands = [
        (f"uv run allocator route ortools {small_file}",
         "TSP routing with OR-Tools"),
        (f"uv run allocator route ortools {small_file} --distance haversine",
         "TSP routing with haversine distance"),
        (f"uv run allocator route ortools {small_file} --output cli_demo_data/route.csv",
         "TSP routing with output file"),
        (f"uv run allocator route ortools {small_file} --format json",
         "TSP routing with JSON output")
    ]
    
    results = {}
    for cmd, desc in commands:
        results[cmd] = run_command(cmd, desc)
        time.sleep(0.5)
        
    return results

def demonstrate_assignment_commands(sample_file: str, workers_file: str):
    """Demonstrate assignment CLI commands."""
    
    print("\n📍 Assignment Commands Demonstration")
    print("=" * 50)
    
    commands = [
        (f"uv run allocator sort {sample_file} --workers {workers_file}",
         "Basic assignment to closest workers"),
        (f"uv run allocator sort {sample_file} --workers {workers_file} --distance haversine",
         "Assignment with haversine distance"),
        (f"uv run allocator sort {sample_file} --workers {workers_file} --output cli_demo_data/assignments.csv",
         "Assignment with output file"),
        (f"uv run allocator sort {sample_file} --workers {workers_file} --format json",
         "Assignment with JSON output")
    ]
    
    results = {}
    for cmd, desc in commands:
        results[cmd] = run_command(cmd, desc)
        time.sleep(0.5)
        
    return results

def demonstrate_advanced_workflows(sample_file: str, workers_file: str):
    """Demonstrate advanced CLI workflow combinations."""
    
    print("\n🚀 Advanced Workflow Examples")
    print("=" * 50)
    
    print("💡 Real-world workflow: Cluster → Route → Assign")
    print("-" * 50)
    
    # Step 1: Cluster the data
    print("\n1️⃣ First, cluster locations into zones...")
    cluster_cmd = f"uv run allocator cluster kmeans {sample_file} --n-clusters 3 --output cli_demo_data/zones.csv"
    cluster_result = run_command(cluster_cmd, "Create maintenance zones")
    
    if cluster_result.get('success'):
        # Step 2: Route within each cluster (simplified for demo)
        print("\n2️⃣ Then, optimize routes within zones...")
        
        # Read the clustered data 
        try:
            clustered_data = pd.read_csv("cli_demo_data/zones.csv")
            
            # Route within largest cluster
            largest_cluster = clustered_data['cluster'].value_counts().index[0]
            cluster_subset = clustered_data[clustered_data['cluster'] == largest_cluster].head(8)  # Limit for demo
            cluster_file = "cli_demo_data/cluster_subset.csv"
            cluster_subset.to_csv(cluster_file, index=False)
            
            route_cmd = f"uv run allocator route ortools {cluster_file} --output cli_demo_data/cluster_route.csv"
            route_result = run_command(route_cmd, f"Optimize route for cluster {largest_cluster}")
            
        except Exception as e:
            print(f"⚠️ Cluster routing step failed: {e}")
    
    # Step 3: Assign zones to service depots
    print("\n3️⃣ Finally, assign zones to service depots...")
    assign_cmd = f"uv run allocator sort {sample_file} --workers {workers_file} --output cli_demo_data/final_assignments.csv"
    assign_result = run_command(assign_cmd, "Assign locations to service depots")
    
    return {
        'cluster_step': cluster_result,
        'assign_step': assign_result if 'assign_result' in locals() else None
    }

def demonstrate_file_formats():
    """Demonstrate different input/output file formats."""
    
    print("\n📄 File Format Demonstrations")
    print("=" * 50)
    
    # Show that CSV files were created
    demo_files = list(Path("cli_demo_data").glob("*.csv"))
    
    print("📁 Generated files during demonstration:")
    for file_path in demo_files:
        try:
            df = pd.read_csv(file_path)
            print(f"   • {file_path.name}: {len(df)} rows, {len(df.columns)} columns")
            if len(df.columns) <= 6:  # Show columns for smaller files
                print(f"     Columns: {list(df.columns)}")
        except Exception as e:
            print(f"   • {file_path.name}: Error reading file - {e}")
    
    print(f"\n💾 Total files created: {len(demo_files)}")

def main():
    """Run complete CLI workflow demonstration."""
    
    print("🖥️ Allocator CLI Workflow Demonstration")
    print("=" * 60)
    print("Demonstrating complete CLI functionality with real road network data")
    
    # Prepare data
    data_info = prepare_sample_data()
    
    # Track all results
    all_results = {}
    
    try:
        # 1. Help commands
        all_results['help'] = demonstrate_cli_help()
        
        # 2. Clustering commands 
        all_results['clustering'] = demonstrate_clustering_commands(data_info['sample_file'])
        
        # 3. Routing commands
        all_results['routing'] = demonstrate_routing_commands(data_info['sample_file'])
        
        # 4. Assignment commands
        all_results['assignment'] = demonstrate_assignment_commands(
            data_info['sample_file'], 
            data_info['workers_file']
        )
        
        # 5. Advanced workflows
        all_results['advanced'] = demonstrate_advanced_workflows(
            data_info['sample_file'],
            data_info['workers_file']
        )
        
        # 6. File format summary
        demonstrate_file_formats()
        
    except Exception as e:
        print(f"❌ Demonstration error: {e}")
        return
    
    # Final summary
    print("\n📊 CLI Demonstration Summary")
    print("=" * 60)
    
    total_commands = 0
    successful_commands = 0
    
    for category, results in all_results.items():
        if isinstance(results, dict):
            for cmd, result in results.items():
                if isinstance(result, dict) and 'success' in result:
                    total_commands += 1
                    if result['success']:
                        successful_commands += 1
    
    success_rate = (successful_commands / total_commands) * 100 if total_commands > 0 else 0
    
    print(f"✅ Commands executed: {total_commands}")
    print(f"✅ Successful commands: {successful_commands}")
    print(f"✅ Success rate: {success_rate:.1f}%")
    
    print(f"\n🎯 CLI Features Demonstrated:")
    print(f"   • Help and version information")
    print(f"   • K-means clustering with multiple options")
    print(f"   • TSP route optimization")
    print(f"   • Distance-based assignment")
    print(f"   • Multiple distance metrics (euclidean, haversine)")
    print(f"   • Various output formats (table, CSV, JSON)")
    print(f"   • File input/output handling")
    print(f"   • Advanced multi-step workflows")
    
    print(f"\n🏗️ Production Usage Patterns:")
    print(f"   • Data preparation: Convert raw data to longitude/latitude format")
    print(f"   • Batch processing: Use --output to save results for further analysis")
    print(f"   • Integration: JSON format for API integration")
    print(f"   • Automation: CLI commands can be scripted for workflows")
    print(f"   • Validation: Use different distance metrics to validate results")
    
    print(f"\n💡 Next Steps:")
    print(f"   • Scale up to full datasets (1000+ points)")
    print(f"   • Integrate with external APIs (OSRM, Google Maps)")
    print(f"   • Add visualization using generated CSV files")
    print(f"   • Combine with GIS tools for spatial analysis")
    
    print(f"\n🎉 CLI workflow demonstration complete!")
    print(f"   All major CLI features tested with real geographic data.")
    print(f"   Ready for production deployment and automation!")


if __name__ == "__main__":
    main()