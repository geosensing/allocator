#!/usr/bin/env python

import sys
import shlex
import argparse

from subprocess import PIPE, Popen

import pandas as pd

from allocator.algorithms import calculate_cluster_statistics


def execute(cmd):
    """
    Execute system command
    """
    p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, close_fds=True)
    out, err = p.communicate()
    return out, err


def main(argv=sys.argv[1:]):

    desc = 'Compare KaHIP vs K-means clustering approaches'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('input', default=None,
                        help='Road segments input file')
    parser.add_argument('-n', '--n_workers', dest='n_workers', type=int, required=True,
                        help='Number of workers')

    parser.add_argument('-d', '--distance-func', default='euclidean',
                        choices=['euclidean', 'haversine', 'osrm'],
                        help='Distance function for distance matrix')

    parser.add_argument('--n-closest', dest='n_closest', type=int, default=10,
                        help='Number of closest edges')
    parser.add_argument('--buffoon', dest='buffoon', action='store_true',
                        help='Use buffoon strategy instead of KaFFPaE')
    parser.set_defaults(buffoon=False)

    parser.add_argument('--balance-edges', dest='balance_edges', action='store_true',
                        help='Use balance edges on all modes')
    parser.set_defaults(balance_edges=False)

    parser.add_argument('-o', '--output', default='compare-output.csv',
                        help='Output file name')

    parser.add_argument('--osrm-base-url', dest='osrm_base_url', default=None,
                        help='Custom OSRM service URL')
    parser.add_argument('--osrm-max-table-size', dest='osrm_max_table_size',
                        default=100, type=int, help='Maximum OSRM table size')

    args = parser.parse_args(argv)

    print(args)

    n_clusters = args.n_workers

    # Prepare KaHIP command
    buffoon = '--buffoon' if args.buffoon else ''
    balance_edges = '--balance-edges' if args.balance_edges else ''

    kahip_cmd = (f"python -m allocator.cluster_kahip -n {n_clusters:d} --n-closest {args.n_closest:d} "
                 f"{buffoon} {balance_edges} {args.input} -o tmpkahip{n_clusters:d}.csv -d {args.distance_func}")

    print(f"KaHIP command line '{kahip_cmd}'")
    out, err = execute(kahip_cmd)
    print(f"Output: {out}")

    # Read KaHIP results and calculate statistics
    bdf = pd.read_csv(f'tmpkahip{n_clusters:d}.csv')
    kahip_stats = calculate_cluster_statistics(
        bdf, 
        bdf['assigned_points'].values - 1,  # Convert to 0-based
        distance_method=args.distance_func,
        osrm_base_url=args.osrm_base_url,
        osrm_max_table_size=args.osrm_max_table_size
    )
    
    adf = pd.DataFrame(kahip_stats)

    # Prepare K-means command
    kmean_cmd = (f'python -m allocator.cluster_kmeans -n {n_clusters:d} {args.input} '
                 f'-o tmpkmean{n_clusters:d}.csv -d {args.distance_func}')

    print(f"K-mean command line '{kmean_cmd}'")
    out, err = execute(kmean_cmd)
    print(f"Output: {out}")

    # Read K-means results and calculate statistics
    kdf = pd.read_csv(f'tmpkmean{n_clusters:d}.csv')
    kmean_stats = calculate_cluster_statistics(
        kdf,
        kdf['assigned_points'].values - 1,  # Convert to 0-based
        distance_method=args.distance_func,
        osrm_base_url=args.osrm_base_url,
        osrm_max_table_size=args.osrm_max_table_size
    )
    
    bdf_kmean = pd.DataFrame(kmean_stats)

    # Combine results
    adf['method'] = 'kahip'
    bdf_kmean['method'] = 'kmeans'
    final_df = pd.concat([adf, bdf_kmean], ignore_index=True)

    # Save comparison results
    final_df.to_csv(args.output, index=False)
    print("Done")


if __name__ == "__main__":
    sys.exit(main())