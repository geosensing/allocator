#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Allocator by Karlsruhe High Quality Partitioning (KaHIP)
"""

import sys
import os
import argparse
import shlex

from random import randint
from subprocess import PIPE, Popen

import pandas as pd

import networkx as nx
import numpy as np

from allocator.distance_matrix import (euclidean_distance_matrix,
                                       haversine_distance_matrix,
                                       osrm_distance_matrix,
                                       google_distance_matrix)


def execute(cmd):
    """Execute external command
    """
    p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, close_fds=True)
    out, err = p.communicate()
    return out, err


def main(argv=sys.argv[1:]):

    desc = 'Allocator by Karlsruhe High Quality Partitioning (KaHIP)'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('input', default=None,
                        help='Road segments input file')
    parser.add_argument('--kahip-dir', default='./KaHIP/src',
                        help='KaHIP directory (Buffoon version)')
    parser.add_argument('--buffoon', action='store_true',
                        help='Using Buffoon')
    parser.set_defaults(buffoon=False)

    parser.add_argument('--n-closest', default=15, type=int,
                        help='Number of closest nodes to build graph')
    parser.add_argument('-s', '--seed', default=randint(0, 0xFFFF),
                        type=int, help='Random seed for KaHIP')
    parser.add_argument('-n', '--n-workers', dest='n_workers', required=True,
                        type=int, help='Number of workers')
    parser.add_argument('-o', '--output', default='cluster-kahip-output.csv',
                        help='Output file name')

    parser.add_argument('-d', '--distance-func', default='euclidean',
                        choices=['euclidean', 'haversine', 'osrm', 'google'],
                        help='Distance function for distance matrix')

    parser.add_argument('--plot', dest='plot', action='store_true',
                        help='Plot the output')
    parser.set_defaults(plot=False)
    parser.add_argument('--save-plot', dest='save_plot', default=None,
                        help='Save plotting to file')

    parser.add_argument('--balance-edges', action='store_true',
                        help='KaFFPaE with balance edges')
    parser.set_defaults(balance_edges=False)

    parser.add_argument('--osrm-base-url', dest='osrm_base_url', default=None,
                        help='Custom OSRM service URL')
    parser.add_argument('--osrm-max-table-size', dest='osrm_max_table_size',
                        default=100, type=int, help='Maximum OSRM table size')

    parser.add_argument('--api-key', default=None,
                        help='Google Map API Key')

    args = parser.parse_args(argv)

    print(args)

    seed = args.seed
    n_clusters = args.n_workers

    df = pd.read_csv(args.input)

    X = df[['start_long', 'start_lat']].as_matrix()

    if args.distance_func == 'euclidean':
        distances = euclidean_distance_matrix(X)
    elif args.distance_func == 'haversine':
        distances = haversine_distance_matrix(X)
    elif args.distance_func == 'osrm':
        distances = osrm_distance_matrix(X,
                                         chunksize=args.osrm_max_table_size,
                                         osrm_base_url=args.osrm_base_url)
    elif args.distance_func == 'google':
        if args.api_key is None:
            print("ERROR: Google Map API key is required,"
                  " please specify by `--api-key`")
            sys.exit(-1)
        distances = google_distance_matrix(X, api_key=args.api_key,
                                           duration=False)
    
    if distances is None:
        print("ERROR: Couldn't get distance matrix of locations")
        sys.exit(-2)

    # FIXME: KaHIP don't like complete graph. Only N closest distances will be
    # used.
    for d in distances:
        s = np.argsort(d)
        for i in s[args.n_closest:]:
            d[i] = 0

    G = nx.from_numpy_matrix(distances)

    if args.buffoon:
        # Using KaHIP with Buffoon version
        # Export Graph to METIS text file format
        # http://people.sc.fsu.edu/~jburkardt/data/metis_graph/metis_graph.html
        with open('metis.graph', 'wb') as f:
            f.write('%d %d 11\n' % (len(G.nodes()), len(G.edges())))
            for n in G.nodes():
                a = ['1']
                for e in G.edges(n, data=True):
                    a.append(str(e[1] + 1))
                    a.append(str(int(e[2]['weight'])))
                f.write(' '.join(a) + '\n')

        os.putenv('LD_LIBRARY_PATH', os.path.join(args.kahip_dir, 'extern/argtable-2.10/lib'))

        buffoon_cmd = 'mpirun -n {k:d} {base:s}/optimized/buffoon metis.graph --seed {seed:d} --k {k:d} --preconfiguration=strong --max_num_threads={k:d}'.format(k=n_clusters, base=args.kahip_dir, seed=seed)

        print("Command line: '{:s}'".format(buffoon_cmd))

        out, err = execute(buffoon_cmd)

        print("Output: {:s}".format(out))

        ldf = pd.read_csv('tmppartition{k:d}'.format(k=n_clusters), header=None)
        ldf.columns = ['assigned_points']

    else:
        # Public version of KaHIP with the Python wrapper
        from kahipwrapper import kaHIP
        ncount = len(G)
        vwgt = None
        xadj = []
        adjcwgt = []
        adjncy = []
        nparts = n_clusters
        imbalance = 0.03
        suppress_output = False
        mode = kaHIP.STRONG
        for n in G.nodes():
            xadj.append(len(adjncy))
            for e in G.edges(n, data=True):
                to = e[1]
                adjncy.append(to)
                w = int(e[2]['weight'])
                adjcwgt.append(w)
        xadj.append(len(adjncy))
        """
        # mininum test
        ncount = 5
        vwgt = None
        xadj = [0,2,5,7,9,12]
        adjcwgt = [1,1,1,1,1,1,1,1,1,1,1,1]
        adjncy = [1,4,0,2,4,1,3,2,4,0,1,3]
        nparts = 2
        imbalance = 0.03
        suppress_output = False
        mode = kaHIP.STRONG
        seed = 0
        """
        if args.balance_edges:
            edgecut, part = kaHIP.kaffpa_balance_NE(ncount, vwgt, xadj,
                                                    adjcwgt, adjncy, nparts,
                                                    imbalance, suppress_output,
                                                    seed, mode)
        else:
            edgecut, part = kaHIP.kaffpa(ncount, vwgt, xadj, adjcwgt, adjncy,
                                         nparts, imbalance, suppress_output,
                                         seed, mode)
        ldf = pd.DataFrame(part)
        ldf.columns = ['assigned_points']

    ldf['assigned_points'] += 1
    odf = df.join(ldf)

    if args.plot or args.save_plot:
        import matplotlib.pyplot as plt
        from matplotlib import colors

        fig = plt.figure(figsize=(16, 16))
        plt.ticklabel_format(useOffset=False)
        cvalues = colors.cnames.values()

        ax = fig.add_subplot(1, 1, 1)
        for k, col in zip(range(n_clusters), cvalues):
            my_members = odf.assigned_points == (k + 1)
            ax.plot(odf[my_members]['start_long'],
                    odf[my_members]['start_lat'], 'w', markerfacecolor=col,
                    marker='*', markersize=10)
        d = args.distance_func.title()
        if args.buffoon:
            ax.set_title('KaHIP (Buffoon) [{0:s}]'.format(d))
        else:
            if args.balance_edges:
                title = 'KaFFPaE (with --balance-edges) [{0:s}]'.format(d)
                ax.set_title(title)
            else:
                title = 'KaFFPaE (without --balance-edges) [{0:s}]'.format(d)
                ax.set_title(title)
        if args.plot:
            plt.show()
        if args.save_plot:
            fig.savefig(args.save_plot)

    odf.to_csv(args.output, index=False)
    print("Done")

if __name__ == "__main__":
    sys.exit(main())
