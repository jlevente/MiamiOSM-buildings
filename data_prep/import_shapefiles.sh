#!/bin/bash

echo 'Importing Large Buildings dataset...'
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom $1"/Large_Buildings_2013.shp"

echo 'Importing Culture Venue dataset...'
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom $1"/Culture_Venue.shp"

echo 'Importing Address dataset...'
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom $1"/Address.shp"

echo 'Importing County Library dataset...'
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom $1"/County_Library.shp"

echo 'Importing College dataset...'
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom $1"/College.shp"

echo 'Importing Block Groups dataset...'
ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom $1"/Block_Groups_2010.shp"