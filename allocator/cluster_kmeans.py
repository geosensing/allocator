#!/usr/bin/env python
"""
Allocator by K-means
"""

import sys
import argparse

import pandas as pd

from allocator.algorithms import kmeans_cluster
from allocator.plotting import plot_clusters


def main(argv=sys.argv[1:]):
    desc = 'Random allocator based on K-Means clustering'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('input', default=None,
                        help='Road segments input file')
    parser.add_argument('-n', '--n_workers', dest='n_workers', type=int, required=True,
                        help='Number of workers')

    parser.add_argument('-d', '--distance-func', default='euclidean',
                        choices=['euclidean', 'haversine', 'osrm'],
                        help='Distance function for distance matrix')

    parser.add_argument('--random-state', dest='random_state', type=int, default=None,
                        help='Random state for reproducible results')

    parser.add_argument('-o', '--output', default='cluster-kmeans-output.csv',
                        help='Output file name')
    parser.add_argument('-c', '--centroids', default='cluster-kmeans-centroids-output.csv',
                        help='Centroids output file name')

    parser.add_argument('--plot', dest='plot', action='store_true',
                        help='Plot the output')
    parser.set_defaults(plot=False)

    parser.add_argument('--save-plot', dest='save_plot', default=None,
                        help='Save plot file name')

    parser.add_argument('--osrm-base-url', dest='osrm_base_url', default=None,
                        help='Custom OSRM service URL')
    parser.add_argument('--osrm-max-table-size', dest='osrm_max_table_size',
                        default=100, type=int, help='Maximum OSRM table size')

    args = parser.parse_args(argv)

    print(args)

    # Read input data
    df = pd.read_csv(args.input)
    n_clusters = args.n_workers

    # Run K-means clustering using pure algorithm function
    result = kmeans_cluster(
        df, 
        n_clusters=n_clusters,
        distance_method=args.distance_func,
        random_state=args.random_state,
        osrm_base_url=args.osrm_base_url,
        osrm_max_table_size=args.osrm_max_table_size
    )

    # Add results to dataframe
    df['assigned_points'] = result['labels'] + 1  # Convert to 1-based indexing

    # Save cluster assignments
    df.to_csv(args.output, index=False)

    # Save centroids
    cdf = pd.DataFrame(result['centroids'], columns=['lon', 'lat'])
    cdf.to_csv(args.centroids, index=False)

    # Print convergence info
    if result['converged']:
        print(f"Converged after {result['iterations']} iterations")
    else:
        print(f"Did not converge after {result['iterations']} iterations")

    # Plot if requested
    if args.plot or args.save_plot:
        title = f'Allocator based on K-Means clustering ({args.distance_func.title()})'
        plot_clusters(
            df, 
            result['labels'], 
            result['centroids'],
            title=title,
            save_path=args.save_plot,
            show=args.plot
        )

    print("Done")


if __name__ == "__main__":
    sys.exit(main())