# Miami-Dade County Large Building Import

Software tools and technical description of the Miami-Dade County Large Building Import process.

More info on the [Wiki](http://wiki.openstreetmap.org/wiki/Miami-Dade_County_Large_Building_Import).

## Prerequisites 

Install `PostgreSQL` with `PostGIS` on your system. You can find some help [here](http://wiki.openstreetmap.org/wiki/PostGIS/Installation#).

You will also need the [`psycopg2`](http://initd.org/psycopg/docs/install.html#install-from-package) python package.

## Data preparation

### Get the data

You can find a sample of Large Buildings dataset in `data_prep/sample`. Upload it to a PostgreSQL db with `data_prep/large_buildings_setup.py` [TODO].

Grab the latest set of OSM buildings with `data_prep/get_recent_osm_buildings.py`.

Import the shapefiles to PostgreSQL with `ogr2ogr`.

```
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -geomfield geom /path/to/file/Large_Buildings_2013.shp

ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -geomfield geom /path/to/file//Culture_Venue.shp

ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -geomfield geom /path/to/file/Address.shp

ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -geomfield geom /path/to/file/County_Library.shp

ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -geomfield geom /path/to/file/College.shp
```

### Geocode addresses

### Spatial overlap

To create set of buildings for bulk upload.

...

