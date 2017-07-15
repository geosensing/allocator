#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shortest path using OSRM trip API
"""

import os
import sys
import argparse

import pandas as pd

import requests
import polyline


def osrm_trip(coords, osrm_base_url=None):
    """List of (lon, lat)

       For more information:
       https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md#trip-service
    """
    points = []
    cost = 0
    duration = 0
    tour = None
    a = ';'.join([','.join(str(c) for c in b) for b in coords])
    if osrm_base_url is None:
        if len(coords) > 100:
            print("ERROR: Maximum locations for public OSRM server is 100")
            return points, cost, duration, tour
        url = ('http://router.project-osrm.org/trip/v1/driving/' + a +
               '?overview=full')
    else:
        url = ('{0!s}/trip/v1/driving/{1!s}?overview=full'
               .format(osrm_base_url, a))

    try:
        r = requests.get(url)
        if r.status_code == 200:
            out = r.json()
            points = polyline.decode(out['trips'][0]['geometry'])
            cost = int(float(out['trips'][0]['distance'] / 1000.0))
            duration = out['trips'][0]['duration']
            waypoints = out['waypoints']
            tour = []
            for w in waypoints:
                tour.append(w['waypoint_index'])
        else:
            data = r.json()
            print("OSRM ERROR code={0!s}, message={0!s}"
                  .format(data['code'], data['message']))
    except Exception as e:
        print("ERROR: {0!s}".format(e))
    return points, cost, duration, tour


def main(argv=sys.argv[1:]):

    desc = 'Shortest Path for across points assigned'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('input', default=None,
                        help='Worker assigned road segments file')
    parser.add_argument('-i', '--init-location', default=None,
                        help='First segment_id to start from each worker')
    parser.add_argument('-o', '--output', default='shortest-path-output.csv',
                        help='Output file name')

    parser.add_argument('--save-map', dest='save_map', default=None,
                        help='Save map to HTML file')

    parser.add_argument('--osrm-base-url', dest='osrm_base_url', default=None,
                        help='Custom OSRM service URL')

    args = parser.parse_args(argv)

    print(args)

    df = pd.read_csv(args.input)

    if args.init_location:
        idf = pd.read_csv(args.init_location)

    if args.save_map:
        import folium
        from folium.features import DivIcon

    output = []
    total_distance = 0
    total_duration = 0

    for i, l in enumerate(sorted(df.assigned_points.unique())):
        adf = df.loc[(df.assigned_points == l), ['start_long', 'start_lat']]
        coords = adf.to_records(index=False)

        points, cost, duration, tour = osrm_trip(coords, args.osrm_base_url)
        if tour:
            N = len(tour)
        else:
            N = len(coords)

        print('TSP: {:d}, Cost: {:d}, Duration: {:0.1f}, N: {:d}'
              .format(l, cost, duration, N))

        total_distance += cost
        total_duration += duration

        B = df.loc[df.assigned_points == l,
                   ['segment_id', 'start_lat', 'start_long']]
        B.reset_index(drop=True, inplace=True)
        if tour:
            B['order'] = tour
            C = B.sort_values(by='order')
            C.reset_index(drop=True, inplace=True)

            path = list(C['segment_id'])
        else:
            path = []

        # Rotate path to start from the initial segments
        if args.init_location:
            start_segment_id = idf.loc[i][0]
            pos = path.index(start_segment_id)
        else:
            pos = 0
        new_path = path[pos:] + path[:pos]
        output.append([l, cost, duration, N,
                       ';'.join([str(p) for p in new_path])])

        if args.save_map:
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
            fname = "{:s}-{:d}{:s}".format(fn, l, fe)
            print("Save map HTML to file '{:s}'".format(fname))
            map_osm.save(fname)

    print("Total distance: {0:.1f}, duration: {1:.1f}".format(total_distance,
                                                              total_duration))

    # save output to file
    print("Save the output file to '{:s}'".format(args.output))
    odf = pd.DataFrame(output, columns=['worker_id', 'distance', 'duration', 'n',
                                        'path_order'])
    odf.to_csv(args.output, index=False)


if __name__ == "__main__":
    sys.exit(main())
