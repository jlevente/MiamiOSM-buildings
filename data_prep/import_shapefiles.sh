#!/bin/bash

ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom $1"/Large_Buildings_2013.shp"

ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom $1"/Culture_Venue.shp"

ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom $1"/Address.shp"

ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom $1"/County_Library.shp"

ogr2ogr -f "PostgreSQL" PG:"host=localhost user=postgres password=postgres dbname=osmbuildings_miami port=5432" -lco GEOMETRY_NAME=geom $1"/College.shp"