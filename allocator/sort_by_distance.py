#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Allocator by sorting distance from known worker location
"""

import sys
import argparse

import pandas as pd
import numpy as np

from allocator.distance_matrix import (euclidean_distance_matrix,
                                       haversine_distance_matrix,
                                       osrm_distance_matrix,
                                       google_distance_matrix)


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

    df = pd.read_csv(args.input)

    cdf = pd.read_csv(args.centroids)

    n_clusters = len(cdf)

    X = df[['start_long', 'start_lat']].as_matrix()
    centroids = cdf[['lon', 'lat']].as_matrix()

    # Calculate the pairwise distances.
    if args.distance_func == 'euclidean':
        distances = euclidean_distance_matrix(X, centroids)
    elif args.distance_func == 'haversine':
        distances = haversine_distance_matrix(X, centroids)
    elif args.distance_func == 'osrm':
        # FIXME: it's duration in OSRM
        distances = osrm_distance_matrix(X, centroids,
                                         chunksize=args.osrm_max_table_size,
                                         osrm_base_url=args.osrm_base_url)
    elif args.distance_func == 'google':
        if args.api_key is None:
            print("ERROR: Google Map API key is required,"
                  " please specify by `--api-key`")
            sys.exit(-1)
        distances = google_distance_matrix(X, centroids,
                                           args.api_key, duration=False)
    
    if distances is None:
        print("ERROR: Couldn't get distance matrix of locations")
        sys.exit(-2)

    colnames = ['distance_{:d}'.format(n + 1) for n in range(n_clusters)]
    dist_df = pd.DataFrame(distances, columns=colnames)

    # join distances
    df = df.join(dist_df)

    # calculate the `order_list_of_workers`
    order_list_of_workers = np.argsort(distances) + 1
    df['order_list_of_workers'] = [';'.join(w.astype(str))
                                   for w in order_list_of_workers]

    # Get minimum distance (duration) to centroids
    known_labels = np.argmin(distances, axis=1)
    df['assigned_points'] = known_labels + 1

    # plot if need
    if args.plot:
        import matplotlib.pyplot as plt
        from matplotlib import colors

        fig = plt.figure(figsize=(8, 8))
        plt.ticklabel_format(useOffset=False)
        cvals = colors.cnames.values()

        ax = fig.add_subplot(1, 1, 1)
        for k, col in zip(range(n_clusters), cvals):
            my_members = known_labels == k
            cluster_center = centroids[k]
            ax.plot(X[my_members, 0], X[my_members, 1], 'w',
                    markerfacecolor=col, marker='.')
            ax.plot(cluster_center[0], cluster_center[1], 'o',
                    markerfacecolor=col, markeredgecolor='k', markersize=6)
        ax.set_title('Allocator based on Known Initial Centroids')
        # ax.set_xticks(())
        # ax.set_yticks(())
        plt.show()

    if args.by_worker:
        output = []
        for l in sorted(df['assigned_points'].unique()):
            colname = 'distance_{:d}'.format(l)
            xdf = df[df.assigned_points == l][['segment_id', colname]]
            xdf.reset_index(drop=True, inplace=True)
            points = xdf.loc[np.argsort(xdf[colname]),
                             'segment_id'].astype(str).tolist()
            output.append([l, ';'.join(points)])
        odf = pd.DataFrame(output, columns=['worker_id', 'segment_ids'])
        odf.to_csv(args.output, index=False)
    else:
        # save output to file
        df.to_csv(args.output, index=False)
    print("Done")


if __name__ == "__main__":
    sys.exit(main())
