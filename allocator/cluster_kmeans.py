#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Allocator by K-means
"""

import sys
import argparse

import pandas as pd
import numpy as np

from allocator.distance_matrix import (euclidean_distance_matrix,
                                       haversine_distance_matrix,
                                       osrm_distance_matrix)


def initialize_centroids(points, k, random_state=None):
    """returns k centroids from the initial points"""
    if random_state:
        rng = np.random.RandomState(random_state)
        rng_state = rng.get_state()
        np.random.set_state(rng_state)
    centroids = points.copy()
    np.random.shuffle(centroids)
    return centroids[:k]


def move_centroids(points, closest, centroids):
    """returns the new centroids assigned from the points closest to them"""
    new_centroids = [points[closest == k].mean(axis=0)
                     for k in range(centroids.shape[0])]
    for i, c in enumerate(new_centroids):
        if np.isnan(c).any():
            new_centroids[i] = centroids[i]
    return np.array(new_centroids)


def closest_centroid_euclidean(points, centroids):
    """returns an array containing the index to the nearest centroid for each
       point
    """
    distances = euclidean_distance_matrix(centroids, points)
    return np.argmin(distances, axis=0)


def closest_centroid_haversine(points, centroids):
    """returns an array containing the index to the nearest centroid for each
       point
    """
    distances = haversine_distance_matrix(centroids, points)
    return np.argmin(distances, axis=0)


def closest_centroid_osrm(points, centroids, args):
    """returns an array containing the index to the nearest centroid for each
       point
    """
    distances = osrm_distance_matrix(centroids, points,
                                     chunksize=args.osrm_max_table_size,
                                     osrm_base_url=args.osrm_base_url)
    return np.argmin(distances, axis=0)


def main(argv=sys.argv[1:]):

    desc = 'Random allocator based on K-Means clustering'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('input', default=None,
                        help='Road segments input file')
    parser.add_argument('-n', '--n_workers', dest='n_workers', required=True,
                        type=int, help='Number of workers')
    parser.add_argument('-m', '--max_iter', default=300,
                        type=int, help='Maximum iteration')
    parser.add_argument('-d', '--distance-func', default='euclidean',
                        choices=['euclidean', 'haversine', 'osrm'],
                        help='Distance function for distance matrix')
    parser.add_argument('-c', '--centroids', default='cluster-kmeans-centroids-output.csv',
                        help='Output file name of K-Means centroids')
    parser.add_argument('-o', '--output', default='cluster-kmeans-output.csv',
                        help='Output file name')

    parser.add_argument('-r', '--random-state', default=None, type=int,
                        help='Random state')

    parser.add_argument('--plot', dest='plot', action='store_true',
                        help='Plot the output')
    parser.set_defaults(plot=False)

    parser.add_argument('--osrm-base-url', dest='osrm_base_url', default=None,
                        help='Custom OSRM service URL')
    parser.add_argument('--osrm-max-table-size', dest='osrm_max_table_size',
                        default=100, type=int, help='Maximum OSRM table size')

    args = parser.parse_args(argv)

    print(args)

    df = pd.read_csv(args.input)

    n_clusters = args.n_workers

    closest_func = {'euclidean': closest_centroid_euclidean,
                    'haversine': closest_centroid_haversine,
                    'osrm': lambda A, B:
                        closest_centroid_osrm(A, B, args)}

    X = df[['start_long', 'start_lat']].values

    centroids = initialize_centroids(X, n_clusters, args.random_state)
    old_centroids = centroids
    i = 0
    while i < args.max_iter:
        i += 1
        print(("Iteration #{0:d}".format(i)))
        closest = closest_func[args.distance_func](X, centroids)
        centroids = move_centroids(X, closest, centroids)
        done = np.all(np.isclose(old_centroids, centroids))
        if done:
            break
        old_centroids = centroids

    cdf = pd.DataFrame(centroids, columns=['lon', 'lat'])

    k_means_labels = closest_func[args.distance_func](X, centroids)

    df['assigned_points'] = k_means_labels + 1

    # plot if need
    if args.plot:
        import matplotlib.pyplot as plt
        from matplotlib import colors

        fig = plt.figure(figsize=(8, 8))
        plt.ticklabel_format(useOffset=False)
        cvalues = list(colors.cnames.values())

        ax = fig.add_subplot(1, 1, 1)
        for k, col in zip(list(range(n_clusters)), cvalues):
            my_members = k_means_labels == k
            cluster_center = centroids[k]
            ax.plot(X[my_members, 0], X[my_members, 1], 'w',
                    markerfacecolor=col, marker='.')
            ax.plot(cluster_center[0], cluster_center[1], 'o',
                    markerfacecolor=col, markeredgecolor='k', markersize=6)
        d = args.distance_func.title()
        ax.set_title('Allocator based on K-Means clustering ({0:s})'.format(d))
        # ax.set_xticks(())
        # ax.set_yticks(())
        plt.show()

    # save output to file
    print(("Saving output to file: {0:s}".format(args.output)))
    df.to_csv(args.output, index=False)

    # save K-Means cetroides to file
    print(("Saving centroids to file: {0:s}".format(args.centroids)))
    cdf.to_csv(args.centroids, index=False, columns=['lat', 'lon'])


if __name__ == "__main__":
    sys.exit(main())
