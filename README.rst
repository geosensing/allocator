allocator: Optimally Allocate Geographically Distributed Tasks
==============================================================

.. image:: https://img.shields.io/pypi/v/allocator.svg
    :target: https://pypi.python.org/pypi/allocator
.. image:: https://pepy.tech/badge/allocator
    :target: https://pepy.tech/project/allocator
.. image:: https://github.com/geosensing/allocator/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/geosensing/allocator/actions/workflows/ci.yml
.. image:: https://img.shields.io/badge/docs-github.io-blue
    :target: https://geosensing.github.io/allocator/

How can we efficiently collect data from geographically distributed locations? If the data 
collection is being crowd-sourced, then we may want to exploit the fact that workers
are geographically distributed. One simple heuristic to do so is to order the locations by 
distance for each worker (with some task registration backend). If you have hired 
workers (or rented drones) who you can send to different locations, then you must split the tasks 
across workers (drones), and plan the 'shortest' routes for each, ala the Traveling Salesman 
Problem (TSP). This is a problem that companies like Fedex etc. solve all the time. Since there 
are no computationally feasible solutions for solving for the global minimum, one heuristic solution 
is to split the locations into clusters of points that are close to each other (ideally, 
we want the clusters to be 'balanced'), and then to estimate a TSP solution for each cluster. 

The package provides a simple way to implement these solutions. Broadly, it provides three kinds of functions:

1. **Sort by Distance:** Produces an ordered list of workers for each point or an ordered list of points 
    for each worker.

2. **Cluster the Points:** Clusters the points into *n_worker* groups.

3. **Shortest Path:** Order points within a cluster (or any small number of points) into a path or itinerary. 

The package also provides access to three different kinds of distance functions for calculating the distance matrices
that underlie these functions: 

1. **Euclidean Distance:** use option ``-d euclidean``; similar to the Haversine distance within the same `UTM zone <https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system>`__)

2. **Haversine Distance:** use option ``-d haversine``. 

3. **OSRM Distance:** use option ``-d osrm``. Neither Haversine nor Euclidean distance take account of the actual road network or the traffic. To use actual travel time, use `Open Source Routing Machine API <http://project-osrm.org/docs/v5.7.0/api/?language=Python#table-service>`__ A maximum number of 100 points can be passed to the function if we use the public server. However, you can set up your own private OSRM server with ``--max-table-size`` to specific the maximum number of points.

4. **Google Distance Matrix API:**. use option ``-d google``. This option available in ``sort_by_distane`` and ``cluster_kahip`` only due to Google Distance Matrix API has very usage limits. Please look at the limitations `here. <https://developers.google.com/maps/documentation/distance-matrix/usage-limits>`__

Downloads
----------
As of February 3rd, 2018, the package had been downloaded nearly 1,700 times (see the `saved BigQuery <https://bigquery.cloud.google.com/savedquery/267723140544:91e63eb83be8482caf1b38da8f62229f>`__).

Related Package
^^^^^^^^^^^^^^^
To sample locations randomly on the streets, check out `geo_sampling <https://github.com/soodoku/geo_sampling>`__.

Application
^^^^^^^^^^^^^^^
Missing Women on the streets of Delhi. See `women count <https://github.com/soodoku/women-count>`__

Install
-------

::

    pip install allocator

Functions
---------

1. `Sort By Distance <allocator/sort_by_distance.py>`__
    
2. **Cluster**
    
    Cluster data collection locations using k-means (clustering) or KaHIP (graph partitioning). To check which of the algorithms produces more cohesive, balanced clusters,
    run `Compare K-means to KaHIP <allocator/compare_kahip_kmeans.py>`__
    
    a. `k-means <allocator/cluster_kmeans.py>`__

        **Examples:**

        ::

            python -m allocator.cluster_kmeans -n 10 allocator/examples/chonburi-roads-1k.csv --plot


    b. `KaHIP allocator <allocator/cluster_kahip.py>`__


3. **Shortest Path**

    These function can be used find the estimated shortest path across all the locations in a cluster. We expose three different ways of getting the 'shortest' path, a) via MST (Christofides algorithm), b) via Google OR-Tools, b) Google Maps Directions API.

    a. `Approximate TSP using MST <allocator/shortest_path_mst_tsp.py>`__

    b. `Google OR Tools TSP solver Shortest path <allocator/shortest_path_ortools.py>`__

    c. `Google Maps Directions API Shortest path <allocator/shortest_path_gm.py>`__ 

    d. `OSRM Trip API Shortest path <allocator/shortest_path_osrm.py>`__ 


Documentation
-------------

Documentation available at: https://allocator.readthedocs.io/en/latest/

Authors
-------

Suriyan Laohaprapanon and Gaurav Sood

Contributor Code of Conduct
---------------------------

The project welcomes contributions from everyone! In fact, it depends on
it. To maintain this welcoming atmosphere, and to collaborate in a fun
and productive way, we expect contributors to the project to abide by
the `Contributor Code of
Conduct <http://contributor-covenant.org/version/1/0/0/>`__.

License
-------

The package is released under the `MIT
License <https://opensource.org/licenses/MIT>`__.
