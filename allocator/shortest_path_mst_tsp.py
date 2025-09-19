#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shortest path using approximate TSP (Christofides's algorithm)
"""

import os
import sys
import argparse
from random import randint

import pandas as pd
import networkx as nx

from Christofides import christofides

from allocator.distance_matrix import (euclidean_distance_matrix,
                                       haversine_distance_matrix,
                                       osrm_distance_matrix)


def main(argv=sys.argv[1:]):

    desc = 'Shortest Path for across points assigned'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('input', default=None,
                        help='Worker assigned road segments file')
    parser.add_argument('-i', '--init-location', default=None,
                        help='First segment_id to start from each worker')
    parser.add_argument('-o', '--output', default='shortest-path-output.csv',
                        help='Output file name')

    parser.add_argument('-d', '--distance-func', default='euclidean',
                        choices=['euclidean', 'haversine', 'osrm'],
                        help='Distance function for distance matrix')

    parser.add_argument('--plot', dest='plot', action='store_true',
                        help='Plot the output')
    parser.set_defaults(plot=False)
    parser.add_argument('--save-plot', dest='save_plot', default=None,
                        help='Save plotting to file')

    parser.add_argument('--osrm-base-url', dest='osrm_base_url', default=None,
                        help='Custom OSRM service URL')
    parser.add_argument('--osrm-max-table-size', dest='osrm_max_table_size',
                        default=100, type=int, help='Maximum OSRM table size')

    args = parser.parse_args(argv)

    print(args)

    df = pd.read_csv(args.input)

    if args.init_location:
        idf = pd.read_csv(args.init_location)

    if args.plot or args.save_plot:
        import matplotlib
        if not args.plot:
            matplotlib.use('agg')
        import matplotlib.pyplot as plt

    output = []
    for i, l in enumerate(sorted(df.assigned_points.unique())):
        print(("Search TSP path for #{:d}...".format(l)))
        A = df.loc[df.assigned_points == l, ['start_long', 'start_lat']].values
        mapping = df.loc[df.assigned_points == l,
                         'segment_id'].reset_index(drop=True).to_dict()
        if args.distance_func == 'euclidean':
            distances = euclidean_distance_matrix(A)
        elif args.distance_func == 'haversine':
            distances = haversine_distance_matrix(A)
        else:
            distances = osrm_distance_matrix(A,
                                             chunksize=args.osrm_max_table_size,
                                             osrm_base_url=args.osrm_base_url)
        G = nx.from_numpy_matrix(distances)
        G = nx.relabel_nodes(G, mapping)
        TSP = christofides.compute(distances)
        tour = TSP['Christofides_Solution']
        if args.distance_func == 'osrm':
            # FIXME: OSRM cost is duration in seconds
            cost = int(TSP['Travel_Cost'])
        else:
            cost = int(TSP['Travel_Cost'] / 1000)
        N = len(tour) - 1
        B = df.loc[df.assigned_points == l, ['segment_id', 'start_long', 'start_lat']]
        B.reset_index(drop=True, inplace=True)
        C = B.loc[tour, :]
        C.reset_index(drop=True, inplace=True)

        if args.plot or args.save_plot:
            fig = plt.figure(figsize=(24, 24))
            plt.ticklabel_format(useOffset=False)
            ax = fig.add_subplot(1, 1, 1)
            ax.plot(C['start_long'],
                    C['start_lat'], 'k', markerfacecolor='#00FF00',
                    marker='.', markersize=10)
            step = 0
            for x, y in zip(C['start_long'], C['start_lat']):
                ox = randint(-24, -16) if randint(0, 1) else randint(16, 24)
                oy = randint(-24, -16) if randint(0, 1) else randint(16, 24)
                ax.annotate(str(step), xy=(x, y), xytext=(ox, oy),
                            textcoords='offset points',
                            arrowprops=dict(arrowstyle="->", color='r'),
                            fontsize=6, color='r')
                step += 1
            ax.set_title('TSP: {:d}, Cost: {:d}, N: {:d}'.format(l, cost, N))
            if args.plot:
                plt.show()
            if args.save_plot:
                fn, fe = os.path.splitext(args.save_plot)
                fname = "{:s}-{:d}{:s}".format(fn, l, fe)
                print(("Plotting to file '{:s}'".format(fname)))
                fig.savefig(fname)
            plt.close()

        # Rotate path to start from the initial segments
        path = list(C['segment_id'])[:-1]
        if args.init_location:
            start_segment_id = idf.loc[i][0]
            pos = path.index(start_segment_id)
        else:
            pos = 0
        new_path = path[pos:] + path[:pos]
        output.append([l, cost, N, ';'.join([str(p) for p in new_path])])

    # save output to file
    print(("Save the output file to '{:s}'".format(args.output)))
    odf = pd.DataFrame(output, columns=['worker_id', 'cost', 'n',
                                        'path_order'])
    odf.to_csv(args.output, index=False)


if __name__ == "__main__":
    sys.exit(main())
