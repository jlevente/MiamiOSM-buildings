import params
import sys
from db_handler import DBHandler
from osm_handler import OSMHandler

def get_args():
    import argparse
    p = argparse.ArgumentParser(description="Data preparation for Miami's OSM Building import")
    p.add_argument('-c', '--create', help='Create Postgres tables', action='store_true')
    p.add_argument('-bd', '--buildings_download', help='Download Buildings from OSM', action='store_true')
    p.add_argument('-ad', '--address_download', help='Download Addresses from OSM', action='store_true')
    p.add_argument('-b', '--bbox', help='BBOX for OSM download (min_lat, min_long, max_lat, max_long). Whole extent of Large buildings is used if left empty')
    p.add_argument('-f', '--fix', help='Fix PostGIS geometry errors', action='store_true')
    p.add_argument('-d', '--dsn', help='Dsn for database connection.')
    p.add_argument('-i', '--intersect', help='Performs intersection of Large Buildings and OSM buildings.')
    p.add_argument('-a', '--assign_address', help='Assigns an address to buildings with only 1 overlapping address point.')
    return p.parse_args()

if __name__ == "__main__":
    args = vars(get_args())
    create = args["instagram"]
    building_download = args["building_download"]
    address_download = args["address_download"]
    fix = args["fix"]
    intersect = args["intersect"]
    address = args["assign_address"]
    bbox = args["bbox"]

    db = DBHandler(dsn)
    osm = OSMHandler(bbox)

    if create:
        db.setup_db()

    if building_download:
        buildings = osm.query_buildings()
        db.upload_buildings()

    if address_download:
        addresses = osm.query_address()
        db.upload_address()

    if fix:
       db.fix_invalid_geom()

    if intersect:
       db.do_intersection()

    if address:
       db.update_address()

    db.close_db_conn()
