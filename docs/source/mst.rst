Minimum Spanning Tree (MST)
===========================

**Input**

- The scripts accepts a CSV file of the initial location (`segment_id`) (see :download:`a sample file <../../allocator/examples/init-location.csv>`) It contains the segment_id of the segment the worker starts data collection from for each worker.
- initial_location (segment_id of the segment the worker starts data collection from)
- output file from 1 or 2 (containing cluster/worker assignments to each point)
- ``--plot`` if you want to see a plot. **Note** Only use if there is a small number of points.

**Output**

- adds a column (path_order) for each worker
- final data:
  + worker_id, path_order
  + xxyy, segment_id_1;segment_id_2, ....segment_id_k

**Usage**

 ::

  usage: shortest_path_mst.py [-h] -i INIT_LOCATION [-o OUTPUT] [--plot] input

  Shortest Path across assigned points

  positional arguments:
    input       Worker assigned road segments file

  optional arguments:
    -h, --help  show this help message and exit
    -i INIT_LOCATION, --init-location INIT_LOCATION
      First segment_id to start collect data of each worker
    -o OUTPUT, --output OUTPUT
      Output file name
    --plot      Plot the output

**Examples**

 ::

  python mst.py -i allocator/examples/init-location.csv allocator/examples/known-centroids-output.csv


Output file will be saved as :download:`mst-shortest-path-output.csv <../../allocator/examples/mst-shortest-path-output.csv>` if file name is not specified by ``-o/--output``
       
 .. image:: ../../allocator/examples/mst-graph.png
   :target: ../../allocator/examples/mst-graph.png
