#!/usr/bin/env python3
"""
Example showing how to use the allocator CLI.
"""

import subprocess
import tempfile
import pandas as pd
from pathlib import Path


def run_cli_example():
    """Demonstrate CLI usage with temporary files."""

    # Create sample data
    data = pd.DataFrame(
        {
            "longitude": [101.0, 101.1, 101.2, 101.3],
            "latitude": [13.0, 13.1, 13.2, 13.3],
            "id": ["Location_A", "Location_B", "Location_C", "Location_D"],
        }
    )

    workers = pd.DataFrame(
        {
            "longitude": [101.05, 101.25],
            "latitude": [13.05, 13.25],
            "worker_id": ["Worker_1", "Worker_2"],
        }
    )

    print("🖥️ Allocator CLI Examples")
    print("=" * 40)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Save test data
        data_file = Path(tmpdir) / "locations.csv"
        workers_file = Path(tmpdir) / "workers.csv"
        data.to_csv(data_file, index=False)
        workers.to_csv(workers_file, index=False)

        print(f"📄 Created test data in {data_file}")
        print(f"📄 Created workers data in {workers_file}")

        print("\n1️⃣ CLI Help:")
        print("   allocator --help")

        print("\n2️⃣ Clustering:")
        print(f"   allocator cluster kmeans {data_file} --n-clusters 2")

        print("\n3️⃣ Routing (TSP):")
        print(f"   allocator route ortools {data_file}")

        print("\n4️⃣ Assignment:")
        print(f"   allocator sort {data_file} --workers {workers_file}")

        print("\n5️⃣ With output file:")
        print(f"   allocator cluster kmeans {data_file} --n-clusters 2 --output clusters.csv")

        print("\n6️⃣ JSON output format:")
        print(f"   allocator sort {data_file} --workers {workers_file} --format json")

        print("\n7️⃣ Different distance metrics:")
        print(f"   allocator cluster kmeans {data_file} --n-clusters 2 --distance haversine")

        print("\n💡 Pro Tips:")
        print("   • Use --verbose for detailed output")
        print("   • All commands support --help for more options")
        print("   • CLI automatically detects CSV, JSON, and GeoJSON files")
        print("   • Results include metadata about the algorithm used")

        print(f"\n🗂️ Test files available in: {tmpdir}")
        print("   (Will be cleaned up automatically)")


if __name__ == "__main__":
    run_cli_example()
