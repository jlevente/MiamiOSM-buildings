import psycopg2
import requests
import json
import psycopg2.extras

def query_buildings():
    # OverpassAPI url
    overpassAPI = 'http://overpass-api.de/api/interpreter'

    # Downtown MIA
    bbox = '25.770098, -80.200582,25.780107,-80.185132'

    postdata = '''
    [out:json][bbox:%s][timeout:120];
    (
      node["building"];
      way["building"];
      relation["building"];
    );
    out geom;
    out meta;
    >;
    '''

    data = requests.post(overpassAPI, postdata % (bbox))
    data = json.loads(data.text)
    return data

def upload_data(data):
    with_no_geom = 0
    sql = 'INSERT INTO osm_buildings (id, type, tags, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326));'
    conn = psycopg2.connect(host='localhost', user='postgres', password='postgres', dbname='osmbuildings_miami')
    psycopg2.extras.register_hstore(conn)
    cursor = conn.cursor()
    for building in data['elements']:
#        print building
        print building['type']
        if building['type'] == 'node':
            cursor.execute(sql, (building['id'], building['type'], building['tags'], 'POINT (' + str(building['lon']) + ' ' + str(building['lat']) + ')'))
        # Upload them as Linestring 
        if building['type'] == 'way':
            geom = 'LINESTRING ('
            try:
                geom += build_wkt_coord_list(building['geometry'])
                geom += ')'
                cursor.execute(sql, (building['id'], building['type'],  building['tags'], geom))
            except KeyError:
                geom += build_wkt_coord_list(get_outer_way(member['ref'])['geometry'])
                geom += ')'
                cursor.execute(sql, (building['id'], building['type'],  building['tags'], geom))
                with_no_geom += 1
                
        # Safe to assume relations are polygons but let's stick to Linestrings. Use only outer as we're interested in spatial overlaps.
        if building['type'] == 'relation':
            geom = 'LINESTRING('
            for member in building['members']:
                if member['role'] == 'outer':
                    geom += build_wkt_coord_list(get_outer_way(member['ref'])['geometry'])
            geom += ')'
            cursor.execute(sql, (building['id'], building['type'],  building['tags'], geom))
        # Upload bounds if it's a multipolygon
        if building['type'] == 'multipolygon':
            bounds = building['bounds']
            lower_left = str(bounds['minlon']) + ' ' + str(bounds['minlat'])
            lower_right = lower_left = str(bounds['maxlon']) + ' ' + str(bounds['minlat'])
            upper_right = str(bounds['maxlon']) + ' ' + str(bounds['maxlat'])
            upper_left = str(bounds['minlon']) + ' ' + str(bounds['maxlat'])
            geom = 'POLYGON((' + lower_left + ',' + lower_right + ',' + upper_right + ',' + upper_left + ',' + lower_left + '))'
            cursor.execute(sql, (building['id'], building['type'],  building['tags'], geom))
    conn.commit()
    print '%s ways without "geometry" block' % with_no_geom

def build_wkt_coord_list(geometry):
    i = 0
    coord_list = ''
    for node in geometry:
        if i > 0:
            coord_list += ', '
        coord_list += str(node['lon']) + ' ' + str(node['lat'])
        i += 1
    return coord_list

def get_outer_way(id):
    overpassAPI = 'http://overpass-api.de/api/interpreter'
    postdata = '''
    [out:json][timeout:25];
    (
        way(%s);
    );
    out geom;
    >;
    '''
    data = requests.post(overpassAPI, postdata % (id))
    data = json.loads(data.text)
    return data['elements'][0]

def main():
    building_data = query_buildings()
    upload_data(building_data)

if __name__ == '__main__':
    main()
