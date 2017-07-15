KaHIP vs. K-Means comparison
============================

**Usage**

::
    
    usage: compare_kahip_kmeans.py [-h] [--kahip-dir KAHIP_DIR] [--buffoon]
                                  [--n-closest N_CLOSEST] [--balance-edges] -n
                                  N_CLUSTERS [-o OUTPUT]
                                  [-d {euclidean,haversine,osrm}]
                                  input

    KaHIP and K-means clustering comparison

    positional arguments:
      input                 Road segments input file

    optional arguments:
      -h, --help            show this help message and exit
      --kahip-dir KAHIP_DIR
                            KaHIP directory
      --buffoon             Using Buffoon
      --n-closest N_CLOSEST
                            Number of closest distances to build Graph
      --balance-edges       KaFFPaE with balance edges
      -n N_CLUSTERS, --n-clusters N_CLUSTERS
                            Number of clusters
      -o OUTPUT, --output OUTPUT
                            Output file name
      -d {euclidean,haversine,osrm}, --distance-func {euclidean,haversine,osrm}
                            Distance function for distance matrix


**Results**
  
KaHIP (Buffoon) vs. K-means:

::

 python -m allocator compare_kahip_kmeans -n 10 --buffoon allocator/examples/delhi-roads-1k.csv -o allocator/examples/compare-kahip-kmeans/compare-buffoon-kmean.csv

:download:`Total weight for each cluster <../../allocator/examples/compare-kahip-kmeans/compare-buffoon-kmean.csv>`

Statistics:

::
    
 label     n_kahip  graph_weight_kahip  mst_weight_kahip    n_kmeans  graph_weight_kmeans  mst_weight_kmeans
 count  10.00000   10.000000     10.000000   10.000000   10.00000010.000000    10.000000
 mean    5.50000  100.000000  28175.200000   67.000000  100.000000   27763.800000    66.600000
 std     3.02765    3.711843   8961.177425   19.200694   27.296723   13188.724863    13.259797
 min     1.00000   90.000000  16514.000000   48.000000   57.000000   11195.000000    49.000000
 25%     3.25000   99.500000  23912.500000   54.500000   78.500000   16630.250000    58.750000
 50%     5.50000  101.500000  26114.000000   59.500000  110.500000   28856.500000    63.000000
 75%     7.75000  102.000000  34841.000000   76.500000  119.000000   30854.000000    78.000000
 max    10.00000  102.000000  44240.000000  101.000000  132.000000   50168.000000    87.000000

KaHIP (without `--balance-edges`) vs. K-means:

::

  python -m allocator compare_kahip_kmeans -n 10 allocator/examples/delhi-roads-1k.csv -o allocator/examples/compare-kahip-kmeans/compare-kaffpae-kmean.csv

:download:`Total weight for each cluster <../../allocator/examples/compare-kahip-kmeans/compare-kaffpae-kmean.csv>`

Statistics:

::
    
 label     n_kahip  graph_weight_kahip  mst_weight_kahip    n_kmeans  graph_weight_kmeans  mst_weight_kmeans
 count  10.00000   10.000000     10.000000   10.000000   10.00000010.000000    10.000000
 mean    4.50000  100.000000  29579.400000   68.100000  100.000000   27796.800000    66.400000
 std     3.02765    5.011099   8294.915996   20.173966   28.007935   13712.065261    12.294534
 min     0.00000   86.000000  18811.000000   47.000000   57.000000   11833.000000    51.000000
 25%     2.25000  101.250000  24170.250000   51.750000   78.500000   16319.750000    56.750000
 50%     4.50000  102.000000  28477.500000   64.000000  107.500000   26507.500000    64.000000
 75%     6.75000  102.000000  35973.500000   76.250000  123.000000   35198.000000    77.500000
 max     9.00000  102.000000  44041.000000  102.000000  134.000000   49309.000000    86.000000


KaHIP (with `--balance-edges`) vs. K-means:

::

  python -m allocator compare_kahip_kmeans -n 10 --balance-edges allocator/examples/delhi-roads-1k.csv -o allocator/examples/compare-kahip-kmeans/compare-kaffpae+balance-edges-kmean.csv

:download:`Total weight for each cluster <../../allocator/examples/compare-kahip-kmeans/compare-kaffpae+balance-edges-kmean.csv>`

Statistics:

::
    
 label     n_kahip  graph_weight_kahip  mst_weight_kahip    n_kmeans  graph_weight_kmeans  mst_weight_kmeans
 count  10.00000   10.000000     10.000000   10.000000   10.00000010.000000    10.000000
 mean    4.50000  100.000000  30667.700000   68.700000  100.000000   28736.200000    66.600000
 std     3.02765   31.756014  13367.928927    6.481598   35.068188   15905.187838    13.866026
 min     0.00000   42.000000   6884.000000   59.000000   39.000000    3884.000000    40.000000
 25%     2.25000   88.250000  23764.000000   65.500000   85.500000   20430.500000    57.750000
 50%     4.50000   92.000000  32325.000000   69.000000  102.500000   27237.000000    66.000000
 75%     6.75000  119.500000  39119.000000   70.750000  120.000000   37552.500000    78.750000
 max     9.00000  147.000000  48740.000000   83.000000  155.000000   56326.000000    84.000000
