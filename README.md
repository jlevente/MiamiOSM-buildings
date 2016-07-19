# Miami-Dade County Large Building Import

**The project is currently in the planning stage. Nothing is permanent yet.**

Software tools and technical description of the Miami-Dade County Large Building Import process.

More info on the [Wiki](http://wiki.openstreetmap.org/wiki/Miami-Dade_County_Large_Building_Import).

The documentation is a mess. Well, it's not really a documentation yet but a collections of notes and ideas during the planning stage. Don't worry. It'll be nice and clean once we're done.

## Prerequisites 

Install `PostgreSQL` with `PostGIS` on your system. You can find some help [here](http://wiki.openstreetmap.org/wiki/PostGIS/Installation#).

You will also need the [`psycopg2`](http://initd.org/psycopg/docs/install.html#install-from-package) python package.

~~Install osmosis with `apt-get install osmosis` on Ubuntu/Debian (other platforms see http://wiki.openstreetmap.org/wiki/Osmosis/Installation).~~

Install `GDAL/OGR` for your system. Used for importing shapefiles to Postgres with `ogr2ogr`.

## Data preparation [Under Construction]

- Create a PostgreSQL database called osmbuildings_miami (make sure user 'postgres' with the password 'postgres' has access to it). I might make this more flexible later because right now this is kind of hardcoded into the source
- Set up the DB (extensions, tables)
```
python data_prep/main.py --setup
```

### Get the data

- Import shapefiles to db. (I store the shapefiles in the data folder. pass it as the first argument)
```
./data_prep/import_shapefiles.sh data
```
- Grab buildings from OverpassAPI (store them in osm_buildings table)
```
python data_prep/main.py --buildings_download
```
- Grab Addresses from OverpassAPI (osm_addresses table)
```
python data_prep/main.py --address_download
```
- Grab highways/railways from OverpassAPI (osm_highway_railway)
```
python data_prem/main.py --roads_download

### Prepare the data for conversion

```
- Add indexes:
```
python data_prep/main.py --index_data
```
- Update db statistics:
```
python data_prep/main.py --vacuum
```
- Fix some geometry errors in Large Buildings
 ```
python data_prep/main.py --fix
 ```
- Spatial intersection between Large Buildings and osm_buildings. Will result in 2 tables - buildings_no_overlap (for the bulk process) and buildings_overlap (for manually merging them with OSM)
```
python data_prep/main.py --intersect
```
- Assign address to 'buildings_no_overlap' where there's 1-1 building-address relation
```
python data_prep/main.py --assign_address
```
- Check if buildings are near existing OSM addresses. Move those that are closer than 30m to manual bucket.
```
python data_prep/main.py --check_address
```
- Check if buildings overlap with OSM roads/rail tracks. Move overlapping ones to manual bucket.
```
python data_prep/main.py --check_road_rail
```
- Check numbers
```
python data_prep/main.py --report
```

You should have 2 tables: `buildings_no_overlap` for the bulk process (i.e. buildings not interfering with existing OSM data) and `buildings_overlap` for the manual process (i.e. buildings that need manual inspection).

## Data conversion

- Clone `ogr2ogr` in parent directory
```
cd ..
sudo apt-get install -y python-gdal python-lxml
git clone --recursive https://github.com/pnorman/ogr2osm
```

- Navigate back to `MiamiOSM-buildings` and convert `buildings_no_overlap` t an *.osm file (manual bucket)
```
cd MiamiOSM-buildings
./data_conversion/generate_osm_file_bulk.sh mia_building_trans.py miami_test_bulk.osm
```

...

~~Now, it's a good idea to create smaller subsets of the data for testing. Let's limit the area to Downtown and create some tables for the truncated data.~~
~~Run the following query for each imported table.~~

```sqlgeomfield
create table large_buildings_test as (
	select * from large_buildings_2013 where
		ST_Intersects(geom, st_setsrid(st_makeenvelope(-80.200582, 25.770098, -80.185132, 25.780107), 4326))
)
```
### Check and Remove or Fix invalid geometries

Check/repair both datasets using `ST_isValidReason()` and `ST_makeValid()`

### Geocode addresses

### Spatial overlap

To create set of buildings for bulk upload.

...

