#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shortest path using Google's ortools TSP solver
"""

import os
import sys
import argparse

import pandas as pd
import numpy as np

from random import randint

from ortools.constraint_solver import pywrapcp
# You need to import routing_enums_pb2 after pywrapcp!
from ortools.constraint_solver import routing_enums_pb2

from allocator.distance_matrix import (euclidean_distance_matrix,
                                       haversine_distance_matrix,
                                       osrm_distance_matrix)


class DistanceMatrix(object):
    """Random matrix."""

    def __init__(self, A, args):
        """Initialize distance matrix."""
        if args.distance_func == 'euclidean':
            distances = euclidean_distance_matrix(A)
        elif args.distance_func == 'haversine':
            distances = haversine_distance_matrix(A)
        elif args.distance_func == 'osrm':
            distances = osrm_distance_matrix(A,
                                             chunksize=args.osrm_max_table_size,
                                             osrm_base_url=args.osrm_base_url)
        (nx, ny) = distances.shape
        self.matrix = {}
        for from_node in range(nx):
            self.matrix[from_node] = {}
            for to_node in range(ny):
                if from_node == to_node:
                    self.matrix[from_node][to_node] = 0
                else:
                    self.matrix[from_node][to_node] = distances[from_node,
                                                                to_node]

    def Distance(self, from_node, to_node):
        return self.matrix[from_node][to_node]


def ortools_tsp(A, args):
    # TSP of size args.tsp_size
    # Second argument = 1 to build a single tour (it's a TSP).
    # Nodes are indexed from 0 to parser_tsp_size - 1, by default the start of
    # the route is node 0.
    tsp_size = len(A)
    routing = pywrapcp.RoutingModel(tsp_size, 1, 0)

    search_parameters = pywrapcp.RoutingModel.DefaultSearchParameters()
    # Setting first solution heuristic (cheapest addition).
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Setting the cost function.
    # Put a callback to the distance accessor here. The callback takes two
    # arguments (the from and to node inidices) and returns the distance
    # between these nodes.
    matrix = DistanceMatrix(A, args)
    matrix_callback = matrix.Distance
    routing.SetArcCostEvaluatorOfAllVehicles(matrix_callback)

    # Solve, returns a solution if any.
#    assignment = routing.SolveWithParameters(search_parameters)
    assignment = routing.Solve()
    path = []
    cost = 0
    if assignment:
        # Solution cost.
        print((assignment.ObjectiveValue()))
        cost = assignment.ObjectiveValue()
        # Inspect solution.
        # Only one route here; otherwise iterate from 0 to
        # routing.vehicles() - 1
        route_number = 0
        node = routing.Start(route_number)
        route = ''
        while not routing.IsEnd(node):
            route += str(node) + ' -> '
            path.append(node)
            node = assignment.Value(routing.NextVar(node))
        route += '0'
        path.append(0)
        print(route)
    else:
        print('No solution found.')

    return cost, path


def do_save_map(args, label, C):
    try:
        import folium
        from folium.features import DivIcon
        import requests
        import polyline

        a = ';'.join([','.join(str(p) for p in ll)
                     for ll in zip(C['start_long'], C['start_lat'])])
        base_url = 'http://router.project-osrm.org/route/v1/driving/'
        url = base_url + a + '?overview=full'
        r = requests.get(url)
        out = r.json()
        points = polyline.decode(out['routes'][0]['geometry'])
        cost = int(float(out['routes'][0]['distance'] / 1000.0))
        duration = out['routes'][0]['duration']
        print(("Route map distance: {:.1f}, duration: {:.1f}"
              .format(cost, duration)))
        # FIXME: unused
        # legs = out['routes'][0]['legs']
        # waypoints = out['waypoints']

        map_osm = folium.Map(location=points[0], zoom_start=12)

        folium.PolyLine(points, color="blue", weight=2.5,
                        opacity=0.5).add_to(map_osm)

        for idx, sid, lat, lon in C[['segment_id',
                                     'start_lat',
                                     'start_long']].itertuples(index=True):
            folium.Marker([lat, lon],
                          popup='{0:d}'.format(sid)).add_to(map_osm)
            html = ('<div style="font-size: 10pt; color: red">{0:d}</div>'
                    .format(idx))
            folium.map.Marker([lat, lon],
                              icon=DivIcon(icon_size=(150, 36),
                                           icon_anchor=(0, 0),
                                           html=html)
                              ).add_to(map_osm)

        fn, fe = os.path.splitext(args.save_map)
        fname = "{:s}-{:d}{:s}".format(fn, label, fe)
        print(("Save map HTML to file '{:s}'".format(fname)))
        map_osm.save(fname)
    except Exception as e:
        print(("Error: Cannot save map to file ({!s})".format(e)))


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
    parser.add_argument('--save-map', dest='save_map', default=None,
                        help='Save map to HTML file')

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
    total_cost = 0
    for i, l in enumerate(sorted(df.assigned_points.unique())):
        print(("Search TSP path for #{:d}...".format(l)))
        adf = df.loc[df.assigned_points == l, ['start_long', 'start_lat']]
        A = adf.values
        # FIXME: OSRM distance matrix actually isn't distance but it's duration
        cost, tour = ortools_tsp(A, args)
        total_cost += cost
        N = len(tour) - 1
        B = df.loc[df.assigned_points == l, ['segment_id',
                                             'start_lat', 'start_long']]
        B.reset_index(drop=True, inplace=True)
        C = B.loc[tour, :]
        C.reset_index(drop=True, inplace=True)

        title = ('TSP: {:d}, Cost: {:0.1f}, N: {:d} ({:s})'
                 .format(l, cost, N, args.distance_func.title()))

        print(title)

        if args.plot or args.save_plot:
            fig = plt.figure(figsize=(16, 16))
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

            ax.set_title(title)

            if args.plot:
                plt.show()
            if args.save_plot:
                fn, fe = os.path.splitext(args.save_plot)
                fname = "{:s}-{:d}{:s}".format(fn, l, fe)
                print(("Plotting to file '{:s}'".format(fname)))
                fig.savefig(fname)
            plt.close()

        if args.save_map:
            do_save_map(args, l, C)

        # Rotate path to start from the initial segments
        path = list(C['segment_id'])[:-1]
        if args.init_location:
            start_segment_id = idf.loc[i][0]
            pos = path.index(start_segment_id)
        else:
            pos = 0
        new_path = path[pos:] + path[:pos]
        output.append([l, cost, N, ';'.join([str(p) for p in new_path])])

    print(("Total cost: {0:.1f}".format(total_cost)))

    # save output to file
    print(("Save the output file to '{:s}'".format(args.output)))
    odf = pd.DataFrame(output, columns=['worker_id', 'cost', 'n',
                                        'path_order'])
    odf.to_csv(args.output, index=False)


if __name__ == "__main__":
    sys.exit(main())
