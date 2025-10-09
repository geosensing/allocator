"""
Distance Matrix
"""
from __future__ import annotations

import os
import math
import time

import numpy as np
import requests
import googlemaps
import utm

from haversine import haversine
from allocator import get_logger

logger = get_logger(__name__)


MAX_DISTANCE_MATRIX_SIZE = 100


def pairwise_distances(X: np.ndarray, Y: np.ndarray | None = None) -> np.ndarray:
    """Pairwise euclidean distance calculation
    """
    if Y is None:
        Y = X
    return np.sqrt(((Y - X[:, np.newaxis])**2).sum(axis=2))


def latlon2xy(lat: float, lon: float) -> list[float]:
    """Transform lat/lon to UTM coordinate

    Args:
        lat (float): WGS latitude
        lon (float): WGS longitude

    Returns:
        [x, y]: UTM x, y coordinate

    """
    utm_x, utm_y, _, _ = utm.from_latlon(lat, lon)

    return [utm_x, utm_y]


def xy2latlog(x: float, y: float, zone_number: int, zone_letter: str | None = None) -> tuple[float, float]:
    """Transform x, y coordinate to lat/lon coordinate

    Args:
        x (float): UTM x coordinate
        y (float): UTM y coorinate
        zone_number (int): x/y zone number
        zone_letter (char): x/y zone letter (optional)
    Returns:
        [lat, lon]: lat/lon coordinate

    """
    lat, lon = utm.to_latlon(x, y, zone_number, zone_letter)
    return (lat, lon)


def euclidean_distance_matrix(X: np.ndarray, Y: np.ndarray | None = None) -> np.ndarray:
    """Euclidean distance matrix calculation
    """
    if Y is None:
        Y = X
    # Transform lat/log matrix to UTM x/y coordinate
    X = np.apply_along_axis(lambda r: latlon2xy(*r), 1, X[:, [1, 0]])
    Y = np.apply_along_axis(lambda r: latlon2xy(*r), 1, Y[:, [1, 0]])
    return pairwise_distances(X, Y)


def haversine_distance_matrix(X: np.ndarray, Y: np.ndarray | None = None) -> np.ndarray:
    """Harversine distance matrix calculation
    """
    if Y is None:
        Y = X
    return np.apply_along_axis(lambda a, b:
                               np.apply_along_axis(haversine, 1, b, a),
                               1, X[:, [1, 0]], Y[:, [1, 0]]) * 1000.0


def osrm_distance_matrix(X, Y=None, chunksize=MAX_DISTANCE_MATRIX_SIZE,
                         osrm_base_url=None):
    """
    Calculate distance matrix of arbitrary size using OSRM

    Credits: https://github.com/stepankuzmin/distance-matrix

    Please note that OSRM distance matrix is in duration in seconds.

    """
    PUBLIC_OSRM_TABLE_API = 'http://router.project-osrm.org/table/v1/driving/'

    if osrm_base_url is None:
        api_base = PUBLIC_OSRM_TABLE_API
    else:
        api_base = "{0!s}/table/v1/driving/".format(osrm_base_url)

    n_X = len(X)
    if Y is None:
        Y = X
    n_Y = len(Y)
    m = chunksize * 1.0
    Xsplits = math.ceil(n_X / m)
    Ysplits = math.ceil(n_Y / m)
    o = None
    count = 0
    for s in np.array_split(X, Xsplits):
        c = None
        for d in np.array_split(Y, Ysplits):
            a = ';'.join([','.join([str(x) for x in b]) for b in (list(s) +
                                                                  list(d))])
            sources = ';'.join([str(k) for k in range(0, len(s))])
            destinations = ';'.join([str(k) for k in range(len(s), len(s) +
                                                           len(d))])
            url = (api_base + a + '?sources=' + sources +
                   '&destinations=' + destinations)
            count += 1
            r = requests.get(url)
            if r.status_code != 200:
                logger.error(f"OSRM Table API request error: {r.text}")
                break
            dm = r.json()['durations']
            arr = np.array(dm)
            if c is None:
                c = arr
            else:
                c = np.concatenate((c, arr), axis=1)
        if o is None:
            o = c
        else:
            o = np.concatenate((o, c), axis=0)
    logger.info(f"Total API requests: {count}")
    return o


def google_distance_matrix(X, Y=None, api_key=None, duration=True):
    """
    Limitations:

    Users of the standard API:
    * 2,500 free elements per day, calculated as the sum of client-side and
      server-side queries.
    * Maximum of 25 origins or 25 destinations per request.
    * 100 elements per request.
    * 100 elements per second, calculated as the sum of client-side and
      server-side queries.

    For more informaton:-
    https://developers.google.com/maps/documentation/distance-matrix/usage-limits
    """

    gmaps = googlemaps.Client(key=api_key, queries_per_second=1)

    n_X = len(X)
    if Y is None:
        Y = X
    n_Y = len(Y)
    nXY = n_X * n_Y
    if nXY > 100:
        # if more than 100 elements per requests
        Xsplits = math.ceil(n_X / 10.0)
        Ysplits = math.ceil(n_Y / 10.0)
    else:
        # if origins more than 25 elements
        if n_X > 25:
            Xsplits = math.ceil(n_X / 25.0)
        else:
            Xsplits = 1
        # if destinations more than 25 elements
        if n_Y > 25:
            Ysplits = math.ceil(n_Y / 25.0)
        else:
            Ysplits = 1
    o = None
    count = 0
    for s in np.array_split(X, Xsplits):
        c = None
        for d in np.array_split(Y, Ysplits):
            sources = [','.join([str(x) for x in b[::-1]]) for b in list(s)]
            destinations = [','.join([str(x) for x in b[::-1]]) for b in list(d)]
            count += 1
            try:
                matrix = gmaps.distance_matrix(sources, destinations)
            except Exception as e:
                logger.error(f"Google Distance Matrix API error: {e}")
                return o
            time.sleep(1)
            """
            FIXME: there are more options for Google
            now = datetime.now()
            matrix = gmaps.distance_matrix(origins, destinations,
                                                mode="driving",
                                                language="en-US",
                                                avoid="tolls",
                                                units="imperial",
                                                departure_time=now,
                                                traffic_model="optimistic")
            """
            rv = []
            for r in matrix['rows']:
                cv = []
                for a in r['elements']:
                    if a['status'] == 'NOT_FOUND':
                        cv.append(-1)
                    else:
                        if duration:
                            cv.append(a['duration']['value'])
                        else:
                            cv.append(a['distance']['value'])
                rv.append(cv)
            arr = np.array(rv)
            if c is None:
                c = arr
            else:
                c = np.concatenate((c, arr), axis=1)
        if o is None:
            o = c
        else:
            o = np.concatenate((o, c), axis=0)
    logger.info(f"Total API requests: {count}, elements: {nXY}")
    return o


if __name__ == "__main__":
    A = [(100.92367939299999, 12.9881022409),
         (100.925755544, 12.9921335249),
         (100.9304806, 13.0083716),
         (100.926791146, 13.043918686400001),
         (100.92598356799999, 13.052921136300002),
         (100.92565068299999, 13.057428131500002),
         (100.92332900000001, 13.070156599999999),
         (100.92668518100001, 13.0471308601),
         (100.928559174, 13.0337361936),
         (100.930720528, 13.0249518827),
         (100.93586505299999, 12.9961366559),
         (100.938816718, 12.9926741168),
         (100.950797781, 12.988299568499999),
         (100.955084343, 12.9896051803),
         (100.95023573200001, 12.9850600191),
         (100.973335173, 12.970164504000001),
         (100.951658295, 12.966859378099999),
         (100.9643745, 12.983327800000001),
         (100.96412451100001, 12.9911421628),
         (100.97528710600001, 12.997597376099998),
         (100.978201259, 13.0008230533),
         (100.9819587, 13.0025727),
         (100.983779719, 13.000793186600001),
         (100.993053018, 13.000876610299999),
         (101.017629001, 13.0063681932),
         (100.99647811700001, 12.9973096012),
         (100.98699825700001, 12.9838055878),
         (100.98185922, 12.9842399301),
         (100.999561162, 12.983644143900001),
         (101.00036104700001, 12.979258225299999),
         (100.971049119, 13.013643913),
         (100.94985559999999, 13.021159800000001),
         (100.95712459999999, 13.026824900000001),
         (100.959937017, 13.037676906),
         (100.972622233, 13.0477065914),
         (100.97665125600001, 13.0495575953),
         (100.98445216799999, 13.0577860656),
         (100.980016815, 13.0582918192),
         (100.97082548899999, 13.058280589),
         (100.9920802, 13.053335800000001)]
    B = [(101.016017474, 13.0480635146),
         (101.007009598, 13.0487060886),
         (100.9981906, 13.0511963),
         (100.996584772, 13.031967748900001),
         (100.996665173, 13.0229307205),
         (100.993143245, 13.002862555899998),
         (100.995907391, 13.011473606900001),
         (100.995850895, 13.0521268678),
         (100.995500145, 13.065663662),
         (101.00306659399999, 13.0740596833),
         (101.007521736, 13.0736980356),
         (101.012072913, 13.0739971207),
         (101.016531338, 13.075093719000002),
         (101.024929665, 13.0729248553),
         (100.99468335899999, 13.072488093699999),
         (100.985483699, 12.9795378991),
         (100.975354886, 12.968618066300001),
         (100.9593403, 12.978952699999999),
         (100.948364611, 12.985934866400001),
         (100.94067286100001, 12.990913086199999),
         (100.93196229, 12.989148296300002),
         (100.92367939299999, 12.9881022409)]

    o = osrm_distance_matrix(A, B, 10)
    logger.debug(f"Matrix sum: {o.sum()}")
    o = osrm_distance_matrix(A, B, 20)
    logger.debug(f"Matrix sum: {o.sum()}")
    o = osrm_distance_matrix(A, B, MAX_DISTANCE_MATRIX_SIZE)
    logger.debug(f"Matrix sum: {o.sum()}")

    api_key = os.environ.get('API_KEY', None)
    if api_key:
        o = google_distance_matrix(A, B, api_key=api_key)
        logger.debug(f"Matrix sum: {o.sum()}")
        # Test with origins over 25 elements
        o = osrm_distance_matrix(A[:30], B[:3], MAX_DISTANCE_MATRIX_SIZE)
        logger.debug(f"Matrix sum: {o.sum()}")
        o = google_distance_matrix(A[:30], B[:3], api_key=api_key)
        logger.debug(f"Matrix sum: {o.sum()}")
    else:
        logger.warning("Please set Google API key to environment variable `API_KEY`")
