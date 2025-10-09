#!/usr/bin/env python
"""
Allocator by sorting distance from known worker location
"""

import sys
import argparse

import pandas as pd
import numpy as np

from allocator.algorithms import sort_by_distance_assignment
from allocator.plotting import plot_assignments


def main(argv=sys.argv[1:]):
    desc = 'Known initial centroids allocator'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('input', default=None,
                        help='Road segments input file')
    parser.add_argument('-c', '--centroids', dest='centroids', required=True,
                        help='Known locations of the workers')
    parser.add_argument('-o', '--output', default='sort-by-distance-output.csv',
                        help='Output file name')

    parser.add_argument('-d', '--distance-func', default='euclidean',
                        choices=['euclidean', 'haversine', 'osrm', 'google'],
                        help='Distance function for distance matrix')

    parser.add_argument('--plot', dest='plot', action='store_true',
                        help='Plot the output')
    parser.set_defaults(plot=False)

    parser.add_argument('--by-worker', dest='by_worker', action='store_true',
                        help='Alternative output format by worker')
    parser.set_defaults(by_worker=False)

    parser.add_argument('--osrm-base-url', dest='osrm_base_url', default=None,
                        help='Custom OSRM service URL')
    parser.add_argument('--osrm-max-table-size', dest='osrm_max_table_size',
                        default=100, type=int, help='Maximum OSRM table size')

    parser.add_argument('--api-key', default=None,
                        help='Google Map API Key')

    args = parser.parse_args(argv)

    print(args)

    # Read input data
    df = pd.read_csv(args.input)
    cdf = pd.read_csv(args.centroids)
    n_clusters = len(cdf)

    X = df[['start_long', 'start_lat']].values
    centroids = cdf[['lon', 'lat']].values

    # Validate API key for Google method
    if args.distance_func == 'google' and args.api_key is None:
        print("ERROR: Google Map API key is required, please specify by `--api-key`")
        sys.exit(-1)

    # Calculate assignments using centralized function
    try:
        labels = sort_by_distance_assignment(
            df,
            centroids,
            distance_method=args.distance_func,
            api_key=args.api_key,
            osrm_base_url=args.osrm_base_url,
            osrm_max_table_size=args.osrm_max_table_size,
            duration=False  # For Google, use distance not duration
        )
    except Exception as e:
        print(f"ERROR: Couldn't calculate distance matrix: {e}")
        sys.exit(-2)

    # Add results to dataframe
    df['assigned_points'] = labels + 1  # Convert to 1-based indexing

    # Create distance columns for compatibility
    from allocator.distance_matrix import get_distance_matrix
    distances = get_distance_matrix(
        X, centroids,
        method=args.distance_func,
        api_key=args.api_key,
        osrm_base_url=args.osrm_base_url,
        osrm_max_table_size=args.osrm_max_table_size,
        duration=False
    )
    
    colnames = [f'distance_{n + 1}' for n in range(n_clusters)]
    dist_df = pd.DataFrame(distances, columns=colnames)
    df = pd.concat([df, dist_df], axis=1)

    # Plot if requested
    if args.plot:
        plot_assignments(df, title=f'Distance-based Assignment ({args.distance_func.title()})')

    # Output handling
    if args.by_worker:
        output = []
        for worker_id in sorted(df['assigned_points'].unique()):
            colname = f'distance_{worker_id}'
            xdf = df[df.assigned_points == worker_id][['segment_id', colname]]
            xdf.reset_index(drop=True, inplace=True)
            points = xdf.loc[np.argsort(xdf[colname]),
                             'segment_id'].astype(str).tolist()
            output.append([worker_id, ';'.join(points)])
        odf = pd.DataFrame(output, columns=['worker_id', 'segment_ids'])
        odf.to_csv(args.output, index=False)
    else:
        # Save standard output
        df.to_csv(args.output, index=False)
    
    print("Done")


if __name__ == "__main__":
    sys.exit(main())