#!/bin/bash

echo "Grabbing latest Florida extract..."
wget http://download.geofabrik.de/north-america/us/florida-latest.osm.pbf

echo "Extracting buildings..."
./../osmosis-new/bin/osmosis --read-pbf file=florida-latest.osm.pbf --bounding-box bottom=25.23561 left=-80.87864 top=25.97467 right=-80.11845 --tf accept-ways building=* --used-node --write-pbf SoFlo_buildings.osm.pbf

echo "Extracting addresses..."
./../osmosis-new/bin/osmosis --read-pbf file=florida-latest.osm.pbf --bounding-box bottom=25.23561 left=-80.87864 top=25.97467 right=-80.11845 --tf accept-nodes addr:housenumber=* -write-pbf SoFlo_addresses.osm.pbf

echo "Merging files..."
./../osmosis-new/bin/osmosis --read-pbf SoFlo_addresses.osm.pbf --read-pbf SoFlo_buildings.osm.pbf --merge --write-pbf SoFlo_buildings_addresses.osm.pbf

echo "Inserting OSM dataset to Postgres..."
./../osmosis-new/bin/osmosis --read-pbf SoFlo_buildings_addresses.osm.pbf --write-pgsql database=osmbuildings_miami user=postgres password=postgres

