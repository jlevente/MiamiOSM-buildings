#!/bin/bash

path=$(pwd)

dsn="PG:dbname=osmbuildings_miami user=postgres password=postgres host=localhost"
translation=$1
sql="SELECT height, objectid, zip, city, pre_dir, st_name, st_type, suf_dir, house_num, geom from buildings_no_overlap"

  while [[ "$path" != "" && ! -e "$path/ogr2osm" ]]; do
    path=${path%/*}
  done

ogr2osm_dir="$path/ogr2osm"
output_name=$2

echo "DB connection: $dsn"
echo "Translation file: $translation"
echo "SQL query to export data from: $sql"
echo "ogr2osm dir: $ogr2osm_dir"
echo "Output name: $output_name"

# echo python $ogr2osm_dir/ogr2osm.py "$dsn" -t $translation -f -o $output_name --sql="\"$sql\""
python $ogr2osm_dir/ogr2osm.py "$dsn" -t $translation -f -o $output_name --sql "$sql"