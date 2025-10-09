#!/usr/bin/env python
"""
Shortest path using Google Direction API
"""

import os
import sys
import argparse
from random import randint

import pandas as pd
import googlemaps
import polyline

from allocator import get_logger

logger = get_logger(__name__)


def main(argv=sys.argv[1:]):

    desc = 'Shortest Path for across points assigned'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('input', default=None,
                        help='Worker assigned road segments file')
    parser.add_argument('-i', '--init-location', default=None,
                        help='First segment_id to start from each worker')
    parser.add_argument('-o', '--output', default='shortest-path-output.csv',
                        help='Output file name')

    parser.add_argument('--plot', dest='plot', action='store_true',
                        help='Plot the output')
    parser.set_defaults(plot=False)
    parser.add_argument('--save-plot', dest='save_plot', default=None,
                        help='Save plotting to file')

    parser.add_argument('--api-key', required=True,
                        help='Google Map API Key')

    args = parser.parse_args(argv)

    logger.debug(f"Arguments: {args}")

    df = pd.read_csv(args.input)

    if args.init_location:
        idf = pd.read_csv(args.init_location)

    if args.plot or args.save_plot:
        import matplotlib
        if not args.plot:
            matplotlib.use('agg')
        import matplotlib.pyplot as plt

    gmaps = googlemaps.Client(key=args.api_key)

    output = []
    for i, l in enumerate(sorted(df.assigned_points.unique())):
        logger.info(f"Google Direction API request for #{l}...")
        start = None
        adf = df.loc[(df.assigned_points == l), ['start_lat', 'start_long']]
        nodes = adf.to_records(index=False).tolist()
        cost = 0
        t_min = 0
        tour = []
        N = len(nodes)
        if N >= 25:
            logger.warning("The maximum allowed location is 24 including origin and destination")
        else:
            start = ', '.join([str(x) for x in nodes[0]])
            waypoints = [', '.join([str(x) for x in n]) for n in nodes[1:]]
            try:
                routes = gmaps.directions(start,
                                          start,
                                          waypoints=waypoints,
                                          optimize_waypoints=True)
                for x in routes:
                    rp = x['overview_polyline']['points']
                    points = polyline.decode(rp)
                    wp = x['waypoint_order']
                    legs = x['legs']
                    t_dist = 0
                    t_time = 0
                    for i, leg in enumerate(legs):
                        d = leg['distance']['value']
                        t_dist += d
                        t = leg['duration']['value']
                        t_time += t
                    break
                cost = int(t_dist / 1000)
                t_min = int(t_time / 60 + 1)
                tour = [0] + [(i + 1) for i in wp] + [0]
            except Exception as e:
                logger.error(f'ERROR: {e}')
        B = df.loc[df.assigned_points == l,
                   ['segment_id', 'start_lat', 'start_long']]
        B.reset_index(drop=True, inplace=True)
        C = B.loc[tour, :]
        C.reset_index(drop=True, inplace=True)

        if args.plot or args.save_plot:
            fig = plt.figure(figsize=(16, 16))
            plt.ticklabel_format(useOffset=False)
            ax = fig.add_subplot(1, 1, 1)
            xdf = pd.DataFrame(points)
            ax.plot(xdf[1],
                    xdf[0], 'k', markerfacecolor='#0000FF',
                    marker='.', markersize=10)
            ax.plot(C['start_long'],
                    C['start_lat'], 'w', linestyle='None',
                    markerfacecolor='#00FF00',
                    marker='*', markersize=10)
            step = 0
            for x, y in zip(C['start_long'], C['start_lat']):
                ox = randint(-24, -16) if randint(0, 1) else randint(16, 24)
                oy = randint(-24, -16) if randint(0, 1) else randint(16, 24)
                ax.annotate(str(step), xy=(x, y), xytext=(ox, oy),
                            textcoords='offset points',
                            arrowprops=dict(arrowstyle="->", color='r'),
                            fontsize=6, color='r')
                step += 1
            ax.set_title('TSP: {:d}, Distance: {:d}, Duration: {:d}, N: {:d}'
                         .format(l, cost, t_min, N))
            if args.plot:
                plt.show()
            if args.save_plot:
                fn, fe = os.path.splitext(args.save_plot)
                fname = "{:s}-{:d}{:s}".format(fn, l, fe)
                logger.debug(f"Plotting to file '{fname}'")
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
        output.append([l, cost, t_min, N,
                       ';'.join([str(p) for p in new_path])])

    # save output to file
    logger.info(f"Saved output file to '{args.output}'")
    odf = pd.DataFrame(output, columns=['worker_id', 'distance', 'duration',
                                        'n', 'path_order'])
    odf.to_csv(args.output, index=False)


if __name__ == "__main__":
    sys.exit(main())
