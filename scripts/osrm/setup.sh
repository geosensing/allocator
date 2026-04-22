#!/bin/bash
set -e

REGION=${1:-"us/california"}
DATA_DIR="$(dirname "$0")/data"

mkdir -p "$DATA_DIR"

echo "Downloading OSM data for: $REGION"
echo "Source: https://download.geofabrik.de/"

PBF_URL="https://download.geofabrik.de/${REGION}-latest.osm.pbf"
PBF_FILE="$DATA_DIR/map.osm.pbf"

if [ ! -f "$PBF_FILE" ]; then
    curl -L -o "$PBF_FILE" "$PBF_URL"
else
    echo "PBF file already exists, skipping download"
fi

echo "Extracting road network..."
docker run --rm -v "$DATA_DIR:/data" osrm/osrm-backend:latest \
    osrm-extract -p /opt/car.lua /data/map.osm.pbf

echo "Partitioning..."
docker run --rm -v "$DATA_DIR:/data" osrm/osrm-backend:latest \
    osrm-partition /data/map.osrm

echo "Customizing..."
docker run --rm -v "$DATA_DIR:/data" osrm/osrm-backend:latest \
    osrm-customize /data/map.osrm

echo "Done! Start the server with:"
echo "  cd $(dirname "$0") && docker compose up -d"
echo ""
echo "Test with:"
echo "  curl 'http://localhost:5000/table/v1/driving/-122.4,37.8;-122.5,37.7'"
