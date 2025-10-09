#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    kahip_cmd = "python -m allocator.cluster_kahip -n {k:d} --n-closest {n_closest:d} \
{buffoon:s} {balance_edges:s} {input:s} -o tmpkahip{k:d}.csv -d {dfunc:s} \
".format(k=n_clusters, input=args.input, n_closest=args.n_closest,
         buffoon=buffoon, balance_edges=balance_edges, dfunc=args.distance_func)

    print(("KaHIP command line '{:s}'".format(kahip_cmd)))
    out, err = execute(kahip_cmd)
    print(("Output: {:s}".format(out)))

    bdf = pd.read_csv('tmpkahip{k:d}.csv'.format(k=n_clusters))

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

    kmean_cmd = 'python -m allocator.cluster_kmeans -n {k:d} {input:s} \
-o tmpkmean{k:d}.csv -d {dfunc:s}'.format(k=n_clusters, input=args.input,
                                          dfunc=args.distance_func)

    print(("K-mean command line '{:s}'".format(kmean_cmd)))
    out, err = execute(kmean_cmd)
    print(("Output: {:s}".format(out)))

    kdf = pd.read_csv('tmpkmean{k:d}.csv'.format(k=n_clusters))

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
