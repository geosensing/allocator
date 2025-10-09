#!/usr/bin/env python

import sys
import shlex
import argparse

from subprocess import PIPE, Popen

import pandas as pd
import networkx as nx

from allocator.distance_matrix import (euclidean_distance_matrix,
                                       haversine_distance_matrix,
                                       osrm_distance_matrix)


def execute(cmd):
    """
    Execute system command
    """
    p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, close_fds=True)
    out, err = p.communicate()
    return out, err


def main(argv=sys.argv[1:]):
    desc = 'KaHIP and K-means clustering comparison'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('input', default=None,
                        help='Road segments input file')

    parser.add_argument('--kahip-dir', default='./KaHIP/src',
                        help='KaHIP directory')
    parser.add_argument('--buffoon', action='store_true',
                        help='Using Buffoon')
    parser.set_defaults(buffoon=False)
    parser.add_argument('--n-closest', default=15, type=int,
                        help='Number of closest distances to build Graph')
    parser.add_argument('--balance-edges', action='store_true',
                        help='KaFFPaE with balance edges')
    parser.set_defaults(balance_edges=False)

    parser.add_argument('-n', '--n-clusters', dest='n_clusters', required=True,
                        type=int, help='Number of clusters')
    parser.add_argument('-o', '--output', default='output-kmean-kahip.csv',
                        help='Output file name')

    parser.add_argument('-d', '--distance-func', default='euclidean',
                        choices=['euclidean', 'haversine', 'osrm'],
                        help='Distance function for distance matrix')

    args = parser.parse_args()

    print(args)

    n_clusters = args.n_clusters

    buffoon = '--buffoon' if args.buffoon else ''
    balance_edges = '--balance-edges' if args.balance_edges else ''

    kahip_cmd = (f"python -m allocator.cluster_kahip -n {n_clusters:d} --n-closest {args.n_closest:d} "
                 f"{buffoon} {balance_edges} {args.input} -o tmpkahip{n_clusters:d}.csv -d {args.distance_func}")

    print(f"KaHIP command line '{kahip_cmd}'")
    out, err = execute(kahip_cmd)
    print(f"Output: {out}")

    bdf = pd.read_csv(f'tmpkahip{n_clusters:d}.csv')

    buffoon_w = []
    for cluster_id in sorted(bdf.assigned_points.unique()):
        X = bdf.loc[bdf.assigned_points == cluster_id, ['start_long', 'start_lat']].values
        n = len(X)
        if args.distance_func == 'euclidean':
            distances = euclidean_distance_matrix(X)
        elif args.distance_func == 'haversine':
            distances = haversine_distance_matrix(X)
        elif args.distance_func == 'osrm':
            distances = osrm_distance_matrix(X)
        if distances is None:
            break
        G = nx.from_numpy_matrix(distances)
        T = nx.minimum_spanning_tree(G)
        gw = int(G.size(weight='weight') / 1000)
        tw = int(T.size(weight='weight') / 1000)
        buffoon_w.append([cluster_id, n, gw, tw])

    adf = pd.DataFrame(buffoon_w, columns=['label', 'n', 'graph_weight',
                                           'mst_weight'])

    kmean_cmd = (f'python -m allocator.cluster_kmeans -n {n_clusters:d} {args.input} '
                 f'-o tmpkmean{n_clusters:d}.csv -d {args.distance_func}')

    print(f"K-mean command line '{kmean_cmd}'")
    out, err = execute(kmean_cmd)
    print(f"Output: {out}")

    kdf = pd.read_csv(f'tmpkmean{n_clusters:d}.csv')

    kmean_w = []
    for cluster_id in sorted(kdf.assigned_points.unique()):
        X = kdf.loc[kdf.assigned_points == cluster_id, ['start_long', 'start_lat']].values
        n = len(X)
        if args.distance_func == 'euclidean':
            distances = euclidean_distance_matrix(X)
        elif args.distance_func == 'haversine':
            distances = haversine_distance_matrix(X)
        elif args.distance_func == 'osrm':
            distances = osrm_distance_matrix(X)
        if distances is None:
            break
        G = nx.from_numpy_matrix(distances)
        T = nx.minimum_spanning_tree(G)
        gw = int(G.size(weight='weight') / 1000)
        tw = int(T.size(weight='weight') / 1000)
        kmean_w.append([cluster_id, n, gw, tw])

    bdf = pd.DataFrame(kmean_w, columns=['label', 'n', 'graph_weight',
                                         'mst_weight'])

    odf = adf.join(bdf[['n', 'graph_weight', 'mst_weight']], lsuffix='_kahip',
                   rsuffix='_kmeans')

    odf.to_csv(args.output, index=False)

    pd.set_option('display.width', 120)
    print((odf.describe()))


if __name__ == "__main__":
    sys.exit(main())
