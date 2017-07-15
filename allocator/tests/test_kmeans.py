import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import animation
from sklearn.metrics.pairwise import pairwise_distances_argmin
from sklearn.cluster import KMeans
from sklearn.neighbors import DistanceMetric
import numpy as np
from shapely.geometry import Point
from functools import partial
import pyproj
from shapely.ops import transform
import utm

from distance_matrix import osrm_distance_matrix


def xform_point(proj, lat, lon):
    p = transform(proj, Point(lon, lat))
    return [p.x, p.y]


def initialize_centroids(points, k):
    """returns k centroids from the initial points"""
    rng = np.random.RandomState(42)
    rng_state = rng.get_state()
    np.random.set_state(rng_state)
    centroids = points.copy()
    np.random.shuffle(centroids)
    return centroids[:k]


def move_centroids(points, closest, centroids):
    """returns the new centroids assigned from the points closest to them"""
    #print closest, centroids
    new_centroids = [points[closest==k].mean(axis=0) for k in range(centroids.shape[0])]
    for i, c in enumerate(new_centroids):
        if np.isnan(c).any():
            new_centroids[i] = centroids[i]
    return np.array(new_centroids)


def closest_centroid_euclidean(points, centroids):
    """returns an array containing the index to the nearest centroid for each
       point
    """
    distances = np.sqrt(((points - centroids[:, np.newaxis])**2).sum(axis=2))
    return np.argmin(distances, axis=0)


def closest_centroid_haversine(points, centroids):
    """returns an array containing the index to the nearest centroid for each
       point
    """
    dist = DistanceMetric.get_metric('haversine')
    points = np.radians(points)
    centroids = np.radians(centroids)
    distances = dist.pairwise(centroids[:, [1, 0]],
                              points[:, [1, 0]]) * 6371000
    return np.argmin(distances, axis=0)


def closest_centroid_osrm(points, centroids):
    """returns an array containing the index to the nearest centroid for each
       point
    """
    distances = osrm_distance_matrix(centroids, points)
    return np.argmin(distances, axis=0)


def init(points, n_workers):
    global centroids, old_centroids
    centroids = initialize_centroids(points, n_workers)
    old_centroids = centroids


def animate(i, closest_func=None, title=''):
    global centroids, old_centroids
    closest = closest_func(points, centroids)
    centroids = move_centroids(points, closest, centroids)
    done = np.all(np.isclose(old_centroids, centroids))
    old_centroids = centroids
    ax.cla()
    ax.set_title(title, size=24)
    ax.text(0.95, 0.01, 'iteration={0:d} ({1!s})'.format((i + 1), done),
            verticalalignment='bottom', horizontalalignment='right',
            transform=ax.transAxes, color='green', fontsize=24)
    ax.scatter(points[:, 0], points[:, 1], c=closest)
    ax.scatter(centroids[:, 0], centroids[:, 1], c='r', s=100)


if __name__ == "__main__":

    np.random.seed(None)

    df = pd.read_csv(sys.argv[1])
    df = df.sample(100, random_state=42)
    df.reset_index(drop=True, inplace=True)

    n_workers = 10

    a, b, zone_x, zone_y = utm.from_latlon(df.ix[0].start_lat,
                                           df.ix[0].start_long)
    utm_zone = "{!s}{!s}".format(zone_x, zone_y)

    wgs2utm = partial(pyproj.transform, pyproj.Proj("+init=EPSG:4326"),
                      pyproj.Proj("+proj=utm +zone={:s}".format(utm_zone)))
    utm2wgs = partial(pyproj.transform, pyproj.Proj("+proj=utm +zone={:s}"
                      .format(utm_zone)), pyproj.Proj("+init=EPSG:4326"))


    df[['x', 'y']] = df[['start_lat', 'start_long']].apply(lambda r: xform_point(wgs2utm, *r), axis=1)

    X = df[['x', 'y']].as_matrix()

    # ================ Scikit-learn Kmeans ====================
    k_means = KMeans(n_clusters=n_workers, random_state=42, n_init=1,
                     init=initialize_centroids(X, n_workers)).fit(X)

    centroids = k_means.cluster_centers_

    k_means_labels = pairwise_distances_argmin(X, centroids)

    fig = plt.figure(figsize=(12, 8))
    cvalues = colors.cnames.values()

    ax = fig.add_subplot(1, 1, 1)
    for k, col in zip(range(n_workers), cvalues):
        my_members = k_means_labels == k
        cluster_center = centroids[k]
        ax.plot(X[my_members, 0], X[my_members, 1], 'w',
                markerfacecolor=col, marker='.', markersize=12)
        ax.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
                markeredgecolor='k', markersize=12)
    ax.set_title('KMeans (Scikit-learn)')

    plt.show()

    cdf = pd.DataFrame(centroids, columns=['x', 'y'])

    # transform back  to WGS coordinate
    cdf[['lon', 'lat']] = cdf[['y', 'x']].apply(lambda r: xform_point(utm2wgs, *r), axis=1)

    cdf.to_csv('output_test_scikit_kmeans_centroids.csv',
               columns=['lat', 'lon'], index=False)

    df['assigned_points'] = k_means_labels + 1

    df.to_csv('output_test_scikit_kmeans.csv', index=False)

    # ================ NumPy Kmeans ====================
    closest_func = {'euclidean': closest_centroid_euclidean,
                    'haversine': closest_centroid_haversine,
                    'osrm': closest_centroid_osrm}

    for d in ['euclidean', 'haversine', 'osrm']:
        if d == 'euclidean':
            points = df[['x', 'y']].as_matrix()
        else:
            points = df[['start_long', 'start_lat']].as_matrix()

        # create a simple animation
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(1, 1, 1)

        anim = animation.FuncAnimation(fig, lambda i:
                                       animate(i, closest_func[d],
                                               'KMeans ({0:s} distance)'
                                               .format(d.title())),
                                       init_func=lambda: init(points,
                                                              n_workers),
                                       frames=20, interval=200, blit=False,
                                       repeat=False)

        anim.save('test_numpy_kmeans_{0:s}.mp4'.format(d))

        plt.show()

        if d == 'euclidean':
            cdf = pd.DataFrame(centroids, columns=['x', 'y'])

            # transform back  to WGS coordinate
            cdf[['lon', 'lat']] = cdf[['y', 'x']].apply(lambda r:
                                                        xform_point(utm2wgs,
                                                                    *r),
                                                        axis=1)
        else:
            cdf = pd.DataFrame(centroids, columns=['lon', 'lat'])

        cdf.to_csv('output_test_numpy_kmeans_{0:s}_centroids.csv'.format(d),
                   columns=['lat', 'lon'], index=False)

        k_means_labels = closest_func[d](points, centroids)

        df['assigned_points'] = k_means_labels + 1

        df.to_csv('output_test_numpy_kmeans_{0:s}.csv'.format(d), index=False)
