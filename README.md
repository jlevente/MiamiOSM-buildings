# Miami-Dade County Large Building Import


Software tools and technical description of the Miami-Dade County Large Building Import process.

More info on the [Wiki](http://wiki.openstreetmap.org/wiki/Miami-Dade_County_Large_Building_Import).

If you'd like to contribute, check out the [**Import Tutorial**](Import_Tutorial.md) and start mapping. All steps required for manually editing buildings are described there. Happy mapping!

![Buildings in MIA](img/buildings_satellite.jpg)


## Prerequisites 

Python 2.7.

Install `PostgreSQL` with `PostGIS` on your system. You can find some help [here](http://wiki.openstreetmap.org/wiki/PostGIS/Installation#).

You will also need the [`psycopg2`](http://initd.org/psycopg/docs/install.html#install-from-package) and `requests` python packages.

Install osmosis with `apt-get install osmosis` on Ubuntu/Debian (other platforms see http://wiki.openstreetmap.org/wiki/Osmosis/Installation).

Install `GDAL/OGR` for your system. Used for importing shapefiles to Postgres with `ogr2ogr`.

PLUS `osmconvert`, `ogr2osm`, ...

Download the data files from here:
```
Large Buildings - http://gis.mdc.opendata.arcgis.com/datasets/1e87b925717747c7b59979caa7779039_1
Address - http://gis.mdc.opendata.arcgis.com/datasets/128dcc2c4cac403dbd1d7440e10fa583_0
```

## Data preparation

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
python data_prep/main.py --roads_download

```
### Prepare the data for conversion

- Add indexes:
```
python data_prep/main.py --index_data
```
- Update db statistics:
```
python data_prep/main.py --vacuum
```
- Spatial intersection between Large Buildings and osm_buildings. Will result in 2 tables - buildings_no_overlap (for the bulk process) and buildings_overlap (for manually merging them with OSM)
```
python data_prep/main.py --intersect
```
- Delete buildings with logical errors (small area, misplaced "whole")
```
python data_prep/main.py --delete_err
```
- Assign address to 'buildings_no_overlap' where there's 1-1 building-address relation
```
python data_prep/main.py --assign_address
```
- Move self intersecting buidlings to manual bucket.
```
python data_prep/main.py --move_self_intersect
```
- Move buildings with shared borders to manual bucket.
```
python data_prep/main.py --move_intersect
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

- Clone `ogr2osm` in parent directory
```
cd ..
sudo apt-get install -y python-gdal python-lxml
git clone --recursive https://github.com/pnorman/ogr2osm
```

- Navigate back to `MiamiOSM-buildings` and convert `buildings_no_overlap` t an *.osm file (manual bucket)
```
cd MiamiOSM-buildings
./data_conversion/generate_osm_files.sh bulk
```

- Generate supplementary files with overlapping buildings and addresses for each block group
```
./data_conversion/generate_osm_files.sh review
```
