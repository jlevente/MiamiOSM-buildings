#!/bin/bash

path=$(pwd)

dsn="PG:dbname=osmbuildings_miami user=postgres password=postgres host=localhost"
translation="mia_building_trans.py"

# Find ogr2osm in parent directories
  while [[ "$path" != "" && ! -e "$path/ogr2osm" ]]; do
    path=${path%/*}
  done

ogr2osm_dir="$path/ogr2osm"

echo "DB connection: $dsn"
echo "Translation file: $translation"
echo "SQL query to export data from: $sql"
echo "ogr2osm dir: $ogr2osm_dir"

if [ "$1" == 'bulk' ]; then
  echo "Generating osm file for Bulk upload..."

  output_name="mia_building_bulk.osm"
  sql="SELECT height, objectid, zip, city, pre_dir, st_name, st_type, suf_dir, house_num, geom from buildings_no_overlap"

  # echo python $ogr2osm_dir/ogr2osm.py "$dsn" -t $translation -f -o $output_name --sql="\"$sql\""
  python $ogr2osm_dir/ogr2osm.py "$dsn" -t $translation -f -o $output_name --sql "$sql"

fi

if [ "$1" == 'review' ]; then
  echo "Generating osm files based on Block Groups..."
  curr_dir=`pwd`;
  while IFS='' read -r objectid; do
    echo  "$objectid"
    # For each block, generate osm file
    # TODO: buildings outside the blocks, buildings intersecting with block boundaries in a separate file
  done < $curr_dir/"data_conversion/block_objectids.csv"

fi