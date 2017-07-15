OSRM Trip API Shortest path
===========================

Calculates the route using the `OSRM Trip API <https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md#trip-service>`__.

**Usage**

::

    usage: shortest_path_osrm.py [-h] [-i INIT_LOCATION] [-o OUTPUT]
                                [--save-map SAVE_MAP]
                                [--osrm-base-url OSRM_BASE_URL]
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
      --save-map SAVE_MAP   Save map to HTML file
      --osrm-base-url OSRM_BASE_URL
                            Custom OSRM service URL


**Examples**

Using OSRM Trip API:

::

    python -m allocator.shortest_path_osrm allocator/examples/chonburi-buffoon-n50.csv --save-map allocator/examples/OSRM-buffoon/chonburi-osrm.html -o allocator/examples/chonburi-buffoon-shortest-osrm.csv

We can see actual route on OpenStreet Map if ``--save-map`` option is specified and will looks like :download:`this. <../../allocator/examples/OSRM-buffoon/chonburi-osrm-1.html>`

:download:`CSV output <../../allocator/examples/chonburi-buffoon-shortest-osrm.csv>`
