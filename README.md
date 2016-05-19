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

... Addresses... [TODO]

### Geocode addresses

### Spatial overlap

To create set of buildings for bulk upload.

...

