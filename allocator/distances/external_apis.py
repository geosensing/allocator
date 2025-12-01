"""
External API integrations for distance calculations (OSRM, Google Maps).
"""

from __future__ import annotations

import logging
import math
import time

import googlemaps
import numpy as np
import requests

logger = logging.getLogger(__name__)

# Constants
MAX_DISTANCE_MATRIX_SIZE = 100


def osrm_distance_matrix(
    X: np.ndarray,
    Y: np.ndarray | None = None,
    chunksize: int = MAX_DISTANCE_MATRIX_SIZE,
    osrm_base_url: str | None = None,
) -> np.ndarray:
    """
    Calculate distance matrix of arbitrary size using OSRM

    Credits: https://github.com/stepankuzmin/distance-matrix

    Please note that OSRM distance matrix is in duration in seconds.

    """
    PUBLIC_OSRM_TABLE_API = "http://router.project-osrm.org/table/v1/driving/"

    if osrm_base_url is None:
        api_base = PUBLIC_OSRM_TABLE_API
    else:
        api_base = f"{osrm_base_url!s}/table/v1/driving/"

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
            a = ";".join([",".join([str(x) for x in b]) for b in (list(s) + list(d))])
            sources = ";".join([str(k) for k in range(0, len(s))])
            destinations = ";".join([str(k) for k in range(len(s), len(s) + len(d))])
            url = api_base + a + "?sources=" + sources + "&destinations=" + destinations
            count += 1
            r = requests.get(url)
            if r.status_code != 200:
                logger.error(f"OSRM Table API request error: {r.text}")
                break
            dm = r.json()["durations"]
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


def google_distance_matrix(
    X: np.ndarray, Y: np.ndarray | None = None, api_key: str | None = None, duration: bool = True
) -> np.ndarray:
    """
    Calculate distance matrix using Google Distance Matrix API.

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
            sources = [",".join([str(x) for x in b[::-1]]) for b in list(s)]
            destinations = [",".join([str(x) for x in b[::-1]]) for b in list(d)]
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
            for r in matrix["rows"]:
                cv = []
                for a in r["elements"]:
                    if a["status"] == "NOT_FOUND":
                        cv.append(-1)
                    else:
                        if duration:
                            cv.append(a["duration"]["value"])
                        else:
                            cv.append(a["distance"]["value"])
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
