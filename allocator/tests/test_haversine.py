import numpy as np
from sklearn.neighbors import DistanceMetric
from sklearn.metrics.pairwise import pairwise_distances

import utm
import pyproj
import pandas as pd
from shapely.geometry import Point
from functools import partial
from shapely.ops import transform

from haversine import haversine


# test data in degree (lat, lon)
X = [[36.4256345, -5.1510261],
     [40.4165, -3.7026],
     [41.4165, -4.7026]]


print("Using haversine package...")
print(haversine(X[0], X[1]))
print(haversine(X[0], X[2]))
print(haversine(X[1], X[2]))

dist = DistanceMetric.get_metric('haversine')

X_radian = np.radians(X)

kms = 6367.0

Y_haversine = kms * dist.pairwise(X_radian)

print('Using scikit-learn...')
print(Y_haversine)


def transform_point(proj, lat, lon):
    p = transform(proj, Point(lon, lat))
    return [p.x, p.y]


df = pd.DataFrame(X, columns=['lat', 'lon'])

# Get UTM zone from first position
a, b, zone_x, zone_y = utm.from_latlon(*X[0])
utm_zone = "{!s}{!s}".format(zone_x, zone_y)

wgs2utm = partial(pyproj.transform, pyproj.Proj("+init=EPSG:4326"),
                  pyproj.Proj("+proj=utm +zone={:s}".format(utm_zone)))

df[['x', 'y']] = df[['lat', 'lon']].apply(lambda r:
                                          transform_point(wgs2utm, *r),
                                          axis=1)

X_utm = df[['x', 'y']].as_matrix()

Y_euclidean = pairwise_distances(X_utm) / 1000.0

print('Project to UTM and using Euclidean...')
print(Y_euclidean)
