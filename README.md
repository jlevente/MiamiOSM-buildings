# Miami-Dade County Large Building Import

**The project is currently in the planning stage. Nothing is permanent yet.**

Software tools and technical description of the Miami-Dade County Large Building Import process.

More info on the [Wiki](http://wiki.openstreetmap.org/wiki/Miami-Dade_County_Large_Building_Import).

The documentation is a mess. Well, it's not really a documentation yet but a collections of notes and ideas during the planning stage. Don't worry. It'll be nice and clean once we're done.

## Prerequisites 

Install `PostgreSQL` with `PostGIS` on your system. You can find some help [here](http://wiki.openstreetmap.org/wiki/PostGIS/Installation#).

You will also need the [`psycopg2`](http://initd.org/psycopg/docs/install.html#install-from-package) python package.

## Data preparation

### Get the data

- Grab the latest set of OSM buildings with `data_prep/get_recent_osm_buildings.py`.
- Download Large Buildings 2013 dataset from Miami-Dade County: `http://gis.mdc.opendata.arcgis.com/datasets/1e87b925717747c7b59979caa7779039_1
Import the following shapefiles to PostgreSQL with `ogr2ogr`.

```
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom /path/to/file/Large_Buildings_2013.shp

ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom /path/to/file//Culture_Venue.shp

ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom /path/to/file/Address.shp

ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom /path/to/file/County_Library.shp

ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom /path/to/file/College.shp
```

Now, it's a good idea to create smaller subsets of the data for testing. Let's limit the area to Downtown and create some tables for the truncated data.
Run the following query for each imported table (except for OSM buildings if you extracted them with `data_prep/get_recent_osm_buildings.py`).

```sqlgeomfield
create table large_buildings_test as (
	select * from large_buildings_2013 where
		ST_Intersects(geom, st_setsrid(st_makeenvelope(-80.200582, 25.770098, -80.185132, 25.780107), 4326))
)
```
### Check and Remove or Fix invalid geometries in both datasets using `ST_isValidReason()` and `ST_

### Geocode addresses

### Spatial overlap

To create set of buildings for bulk upload.

...

