"""
External API integrations for distance calculations (OSRM, Google Maps).
"""

import logging
import math
import os
import time
from collections.abc import Callable

import googlemaps
import numpy as np
import requests
from google.maps import routing_v2

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int, str | None], None]

MAX_DISTANCE_MATRIX_SIZE = 100


def osrm_distance_matrix(
    X: np.ndarray,
    Y: np.ndarray | None = None,
    chunksize: int = MAX_DISTANCE_MATRIX_SIZE,
    osrm_base_url: str | None = None,
    on_progress: ProgressCallback | None = None,
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
    total_chunks = Xsplits * Ysplits
    o = None
    chunk_idx = 0
    for s in np.array_split(X, Xsplits):
        c = None
        for d in np.array_split(Y, Ysplits):
            chunk_idx += 1
            a = ";".join([",".join([str(x) for x in b]) for b in (list(s) + list(d))])
            sources = ";".join([str(k) for k in range(0, len(s))])
            destinations = ";".join([str(k) for k in range(len(s), len(s) + len(d))])
            url = api_base + a + "?sources=" + sources + "&destinations=" + destinations
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
            if on_progress:
                on_progress(chunk_idx, total_chunks, None)
        if o is None:
            o = c
        else:
            o = np.concatenate((o, c), axis=0)
    logger.info(f"Total API requests: {chunk_idx}")
    return o


def google_distance_matrix(
    X: np.ndarray,
    Y: np.ndarray | None = None,
    api_key: str | None = None,
    duration: bool = True,
    on_progress: ProgressCallback | None = None,
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
    total_chunks = Xsplits * Ysplits
    o = None
    chunk_idx = 0
    for s in np.array_split(X, Xsplits):
        c = None
        for d in np.array_split(Y, Ysplits):
            chunk_idx += 1
            sources = [",".join([str(x) for x in b[::-1]]) for b in list(s)]
            destinations = [",".join([str(x) for x in b[::-1]]) for b in list(d)]
            try:
                matrix = gmaps.distance_matrix(sources, destinations)
            except Exception as e:
                logger.error(f"Google Distance Matrix API error: {e}")
                return o
            time.sleep(1)
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
            if on_progress:
                on_progress(chunk_idx, total_chunks, None)
        if o is None:
            o = c
        else:
            o = np.concatenate((o, c), axis=0)
    logger.info(f"Total API requests: {chunk_idx}, elements: {nXY}")
    return o


TRAVEL_MODE_MAP = {
    "DRIVE": routing_v2.RouteTravelMode.DRIVE,
    "BICYCLE": routing_v2.RouteTravelMode.BICYCLE,
    "WALK": routing_v2.RouteTravelMode.WALK,
    "TWO_WHEELER": routing_v2.RouteTravelMode.TWO_WHEELER,
    "TRANSIT": routing_v2.RouteTravelMode.TRANSIT,
}


def google_routes_distance_matrix(
    X: np.ndarray,
    Y: np.ndarray | None = None,
    credentials_file: str | None = None,
    duration: bool = True,
    travel_mode: str = "DRIVE",
    on_progress: ProgressCallback | None = None,
) -> np.ndarray:
    """
    Calculate distance matrix using Google Routes API (official client).

    This uses the official google-maps-routing library which handles
    rate limiting and retries automatically.

    Authentication: Set GOOGLE_APPLICATION_CREDENTIALS environment variable
    to your service account JSON file path, or pass credentials_file parameter.

    To set up:
    1. Create a service account in Google Cloud Console
    2. Download the JSON key file
    3. Enable "Routes API" for your project
    4. Either set GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
       or pass credentials_file="/path/to/key.json"

    Args:
        X: Origin coordinates as numpy array with shape [n, 2] where columns are [lon, lat]
        Y: Destination coordinates (optional, defaults to X)
        credentials_file: Path to service account JSON file (optional if
            GOOGLE_APPLICATION_CREDENTIALS is set)
        duration: If True, return duration in seconds; if False, return distance in meters
        travel_mode: One of "DRIVE", "BICYCLE", "WALK", "TWO_WHEELER", "TRANSIT"
        on_progress: Optional callback for progress reporting

    Returns:
        Distance matrix as numpy array with shape [len(X), len(Y)]
    """
    MAX_ORIGINS = 25
    MAX_DESTINATIONS = 25

    if credentials_file:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file

    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        raise ValueError(
            "Google Routes API requires authentication. Either:\n"
            "1. Set GOOGLE_APPLICATION_CREDENTIALS environment variable to your "
            "service account JSON file path, or\n"
            "2. Pass credentials_file='/path/to/service-account.json'"
        )

    if Y is None:
        Y = X

    n_X, n_Y = len(X), len(Y)
    Xsplits = math.ceil(n_X / MAX_ORIGINS) if n_X > 0 else 1
    Ysplits = math.ceil(n_Y / MAX_DESTINATIONS) if n_Y > 0 else 1
    total_chunks = Xsplits * Ysplits
    chunk_idx = 0

    result = np.zeros((n_X, n_Y))
    x_offset = 0

    client = routing_v2.RoutesClient()
    route_travel_mode = TRAVEL_MODE_MAP.get(travel_mode, routing_v2.RouteTravelMode.DRIVE)

    for s in np.array_split(X, Xsplits):
        y_offset = 0
        for d in np.array_split(Y, Ysplits):
            chunk_idx += 1

            origins = [
                routing_v2.RouteMatrixOrigin(
                    waypoint=routing_v2.Waypoint(
                        location=routing_v2.Location(
                            lat_lng={"latitude": float(lat), "longitude": float(lon)}
                        )
                    )
                )
                for lon, lat in s
            ]

            destinations = [
                routing_v2.RouteMatrixDestination(
                    waypoint=routing_v2.Waypoint(
                        location=routing_v2.Location(
                            lat_lng={"latitude": float(lat), "longitude": float(lon)}
                        )
                    )
                )
                for lon, lat in d
            ]

            request = routing_v2.ComputeRouteMatrixRequest(
                origins=origins,
                destinations=destinations,
                travel_mode=route_travel_mode,
            )

            metadata = [
                (
                    "x-goog-fieldmask",
                    "originIndex,destinationIndex,duration,distanceMeters,condition",
                ),
            ]

            for element in client.compute_route_matrix(request=request, metadata=metadata):
                if element.condition == routing_v2.RouteMatrixElementCondition.ROUTE_EXISTS:
                    oi = element.origin_index
                    di = element.destination_index
                    if duration:
                        val = element.duration.total_seconds()
                    else:
                        val = element.distance_meters
                    result[x_offset + oi, y_offset + di] = val

            if on_progress:
                on_progress(chunk_idx, total_chunks, None)

            y_offset += len(d)
        x_offset += len(s)

    logger.info(f"Total API requests: {chunk_idx}, elements: {n_X * n_Y}")
    return result
