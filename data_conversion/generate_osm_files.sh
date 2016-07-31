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
echo "ogr2osm dir: $ogr2osm_dir"

if [ "$1" == 'bulk' ]; then
  echo "Generating osm file for Bulk upload..."
  
  mkdir -p bulk
  out_folder='bulk'

  step=5000
  for (( cnt=0; cnt<=100000; cnt+=step )); do
    echo $cnt
    output_name="mia_building_bulk_"$cnt".osm"
    max_id=$cnt+$step
    sql="SELECT height, objectid, zip, city, pre_dir, st_name, st_type, suf_dir, house_num, geom from buildings_no_overlap where objectid >= $cnt and objectid < $max_id"

    python $ogr2osm_dir/ogr2osm.py "$dsn" -t $translation -f -o $out_folder"/"$output_name --sql "$sql"
  done

fi

if [ "$1" == 'review' ]; then
  echo "Generating osm files based on Block Groups..."
  curr_dir=`pwd`;
  mkdir -p blocks
  out_folder='blocks'

  while IFS='' read -r objectid; do
    # echo  "$objectid"
    output_name=$objectid"_building.osm"
    translation="mia_building_trans.py"

    # Get buildings
    sql="SELECT b.height, b.objectid, b.geom from buildings_overlap b, block_groups_2010 block where st_within(b.geom, block.geom) and block.objectid=$objectid"
    python $ogr2osm_dir/ogr2osm.py "$dsn" -t $translation -f -o $out_folder"/"$output_name --sql "$sql" --id="-1"

    # Get address
    translation="mia_address_trans.py"
    output_name=$objectid"_address.osm"
    sql="SELECT a.objectid, zip, mailing_mu as city, pre_dir, st_name, st_type, suf_dir, hse_num as house_num, a.geom from address a,
      (SELECT b.geom from buildings_overlap b, block_groups_2010 block where
      st_within(b.geom,block.geom) and block.objectid=$objectid) x where st_within(a.geom, x.geom)"
    python $ogr2osm_dir/ogr2osm.py "$dsn" -t $translation -f -o $out_folder"/"$output_name --sql "$sql" --id="-20001"

    # Fake version, timestamps
    osmconvert $out_folder"/"$objectid"_building.osm" --fake-author -o=$out_folder"/"$objectid"_building_fake.osm"
    osmconvert $out_folder"/"$objectid"_address.osm" --fake-author -o=$out_folder"/"$objectid"_address_fake.osm"

    # Sort and merge
    osmosis --read-xml $out_folder"/"$objectid"_address_fake.osm" --sort type="TypeThenId" --write-xml $out_folder"/"$objectid"_address_sort.osm"
    osmosis --read-xml $out_folder"/"$objectid"_building_fake.osm" --sort type="TypeThenId" --write-xml $out_folder"/"$objectid"_building_sort.osm"
    osmosis --read-xml $out_folder"/"$objectid"_building_sort.osm" --read-xml $out_folder"/"$objectid"_address_sort.osm" --merge --write-xml $out_folder"/mia_building_"$objectid".osm"

    # Cleanup
    rm $out_folder"/"$objectid"_building.osm" $out_folder"/"$objectid"_building_fake.osm" $out_folder"/"$objectid"_building_sort.osm" $out_folder"/"$objectid"_address.osm" $out_folder"/"$objectid"_address_fake.osm" $out_folder"/"$objectid"_address_sort.osm"

    ### TODO: get those outside of block groups

  done < $curr_dir/"data_conversion/block_objectids.csv"

  echo '\nGenerating extra osm files for special cases...\n'
  # Get buildings outside blocks

  output_name="building_outside.osm"
  translation="mia_building_trans.py"

  sql="SELECT b.height, b.objectid, b.geom from buildings_overlap b, (select st_union(geom) as geom from block_groups_2010) block where not st_intersects(b.geom, block.geom)"
  python $ogr2osm_dir/ogr2osm.py "$dsn" -t $translation -f -o $out_folder"/"$output_name --sql "$sql" --id="-1"

  # Get address
  translation="mia_address_trans.py"
  output_name="address_outside.osm"

  sql="SELECT a.objectid, zip, mailing_mu as city, pre_dir, st_name, st_type, suf_dir, hse_num as house_num, a.geom from address a,
      (SELECT b.geom from buildings_overlap b, (select st_union(geom) as geom from block_groups_2010) block where
      not st_intersects(b.geom,block.geom)) x where st_within(a.geom, x.geom)"
  python $ogr2osm_dir/ogr2osm.py "$dsn" -t $translation -f -o $out_folder"/"$output_name --sql "$sql" --id="-20001"

  # Fake version, timestamps
  osmconvert $out_folder"/building_outside.osm" --fake-author -o=$out_folder"/building_outside_fake.osm"
  osmconvert $out_folder"/address_outside.osm" --fake-author -o=$out_folder"/address_outside_fake.osm"

  # Sort and merge
  osmosis --read-xml $out_folder"/address_outside_fake.osm" --sort type="TypeThenId" --write-xml $out_folder"/address_outside_sort.osm"
  osmosis --read-xml $out_folder"/building_outside_fake.osm" --sort type="TypeThenId" --write-xml $out_folder"/building_outside_sort.osm"
  osmosis --read-xml $out_folder"/building_outside_sort.osm" --read-xml $out_folder"/address_outside_sort.osm" --merge --write-xml $out_folder"/outside.osm"

  # Get buildings overlapping with block boundaries (i.e. share space with 2 blocks)

  output_name="building_border.osm"
  translation="mia_building_trans.py"

  sql="SELECT b.height, b.objectid, b.geom from buildings_overlap b, (select geom as geom from block_groups_2010) block where st_overlaps(b.geom, block.geom) and not st_within(b.geom, block.geom)"
  python $ogr2osm_dir/ogr2osm.py "$dsn" -t $translation -f -o $out_folder"/"$output_name --sql "$sql" --id="-1"

  # Get address
  translation="mia_address_trans.py"
  output_name="address_border.osm"

  sql="SELECT a.objectid, zip, mailing_mu as city, pre_dir, st_name, st_type, suf_dir, hse_num as house_num, a.geom from address a,
      (SELECT b.geom from buildings_overlap b, (select geom as geom from block_groups_2010) block where
       st_overlaps(b.geom, block.geom) and not st_within(b.geom, block.geom)) x where st_within(a.geom, x.geom)"
  python $ogr2osm_dir/ogr2osm.py "$dsn" -t $translation -f -o $out_folder"/"$output_name --sql "$sql" --id="-20001"

  # Fake version, timestamps
  osmconvert $out_folder"/building_border.osm" --fake-author -o=$out_folder"/building_border_fake.osm"
  osmconvert $out_folder"/address_border.osm" --fake-author -o=$out_folder"/address_border_fake.osm"

  # Sort and merge
  osmosis --read-xml $out_folder"/address_border_fake.osm" --sort type="TypeThenId" --write-xml $out_folder"/address_border_sort.osm"
  osmosis --read-xml $out_folder"/building_border_fake.osm" --sort type="TypeThenId" --write-xml $out_folder"/building_border_sort.osm"
  osmosis --read-xml $out_folder"/building_border_sort.osm" --read-xml $out_folder"/address_border_sort.osm" --merge --write-xml $out_folder"/border.osm"

   # Cleanup
    rm $out_folder"/building_border.osm" $out_folder"/building_border_fake.osm" $out_folder"/building_border_sort.osm" $out_folder"/address_border.osm" $out_folder"/address_border_fake.osm" $out_folder"/address_border_sort.osm" $out_folder"/building_outside.osm" $out_folder"/building_outside_fake.osm" $out_folder"/building_outside_sort.osm" $out_folder"/address_outside.osm" $out_folder"/address_outside_fake.osm" $out_folder"/address_outside_sort.osm"

fi
