Approximate TSP using MST
============================

    
Shortest path based on Minimum Spanning Tree using the `Christofides algorithm for Minimum Spanning Tree <https://en.wikipedia.org/wiki/Christofides_algorithm>`__

**Usage**

::

    usage: shortest_path_mst_tsp.py [-h] [-i INIT_LOCATION] [-o OUTPUT]
                                    [-d {euclidean,haversine,osrm}] [--plot]
                                    [--save-plot SAVE_PLOT]
                                    [--osrm-base-url OSRM_BASE_URL]
                                    [--osrm-max-table-size OSRM_MAX_TABLE_SIZE]
                                    input

    Shortest Path for across points assigned

    positional arguments:
    input                 Worker assigned road segments file

    optional arguments:
    -h, --help            show this help message and exit
    -i INIT_LOCATION, --init-location INIT_LOCATION
                            First segment_id to start from each worker
    -o OUTPUT, --output OUTPUT
                            Output file name
    -d {euclidean,haversine,osrm}, --distance-func {euclidean,haversine,osrm}
                            Distance function for distance matrix
    --plot                Plot the output
    --save-plot SAVE_PLOT
                            Save plotting to file
    --osrm-base-url OSRM_BASE_URL
                            Custom OSRM service URL
    --osrm-max-table-size OSRM_MAX_TABLE_SIZE
                            Maximum OSRM table size


**Examples**

Using KaHIP, we first partition the locations into 50 clusters:

::

    python -m allocator.cluster_kahip -n 50 --n-closest 5 --buffoon allocator/examples/delhi-roads-1k.csv -o allocator/examples/delhi-buffoon-n50.csv

Then we run the script to solve TSP for each cluster:

::

    python -m allocator.shortest_path_mst_tsp allocator/examples/delhi-buffoon-n50.csv --save-plot allocator/examples/TSP-buffoon/delhi-tsp.svg -o allocator/examples/delhi-buffoon-shortest.csv

Please look at the path :download:`here <../../allocator/examples/TSP-buffoon/delhi-tsp-1.svg>`

Using K-means, we first cluster the locations into 50 clusters:

::

    python -m allocator.cluster_kmeans -n 50 allocator/examples/delhi-roads-1k.csv -o allocator/examples/delhi-kmeans-n50.csv

Run the script to solve TSP for each cluster:

::

    python -m allocator.shortest_path_mst_tsp allocator/examples/delhi-kmeans-n50.csv --save-plot allocator/examples/TSP-kmeans/delhi-tsp.svg -o allocator/examples/delhi-kmeans-shortest.csv

Please look at the path :download:`here <../../allocator/examples/TSP-kmeans/delhi-tsp-1.svg>`
