CREATE EXTENSION postgis;
CREATE EXTENSION hstore;
CREATE TABLE osm_buildings (
    id bigint,
    type varchar,
    tags hstore
    );
-- Use generic GEOMETRY type so we can store nodes and ways together
SELECT AddGeometryColumn('osm_buildings', 'geom', 4326, 'GEOMETRY', 2);