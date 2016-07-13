import psycopg2
import requests
import json
import psycopg2.extras

def query_buildings():
    # OverpassAPI url
    overpassAPI = 'http://overpass-api.de/api/interpreter'

    # Downtown MIA
    bbox = '25.770098, -80.200582,25.780107,-80.185132'
    # Extent of Large Building Footprints dataset
    bbox = '25.23561, -80.87864, 25.97467, -80.11845'

    postdata = '''
    [out:json][bbox:%s][timeout:120];
    (
      node["building"];
      relation["building"];
      way["building"];
    );
    out geom;
    out meta;
    >;
    '''

    data = requests.post(overpassAPI, postdata % (bbox))
    data = json.loads(data.text)
    return data

def query_address():
    # OverpassAPI url
    overpassAPI = 'http://overpass-api.de/api/interpreter'

    # Downtown MIA
    bbox = '25.770098, -80.200582,25.780107,-80.185132'
    # Extent of Large Building Footprints dataset
    bbox = '25.23561, -80.87864, 25.97467, -80.11845'

    postdata = '''
    [out:json][bbox:%s][timeout:120];
    (
      node["addr:housenumber"];
    );
    out geom;
    out meta;
    >;
    '''

    data = requests.post(overpassAPI, postdata % (bbox))
    data = json.loads(data.text)
    return data

def upload_address(data):
    sql = 'INSERT INTO osm_addresses (id, type, tags, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326));'
    conn = psycopg2.connect(host='localhost', user='postgres', password='postgres', dbname='osmbuildings_miami')
    psycopg2.extras.register_hstore(conn)
    cursor = conn.cursor()
    for poi in data['elements']:
#        print building
        print poi['type'],  poi['id']
        if poi['type'] == 'node':
            cursor.execute(sql, (poi['id'], poi['type'], poi['tags'], 'POINT (' + str(poi['lon']) + ' ' + str(poi['lat']) + ')'))
    conn.commit()

def upload_buildings(data):
    with_no_geom = 0
    sql = 'INSERT INTO osm_buildings_relations (id, type, tags, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326));'
    conn = psycopg2.connect(host='localhost', user='postgres', password='postgres', dbname='osmbuildings_miami')
    psycopg2.extras.register_hstore(conn)
    cursor = conn.cursor()
    for building in data['elements']:
#        print building
        print building['type'],  building['id']
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
                continue
                
        # Safe to assume relations are polygons but let's stick to Linestrings. Use only outer as we're interested in spatial overlaps.
        if building['type'] == 'relation':
            geom = 'LINESTRING('
            membercnt = 0
            for member in building['members']:
                if member['role'] == 'outer':
                    membercnt += 1
            if membercnt > 1:
                # it's already been returned if there's no bounds... passing
                try:
                    bounds = building['bounds']
                except KeyError:
                    continue
                lower_left = str(bounds['minlon']) + ' ' + str(bounds['minlat'])
                lower_right = str(bounds['maxlon']) + ' ' + str(bounds['minlat'])
                upper_right = str(bounds['maxlon']) + ' ' + str(bounds['maxlat'])
                upper_left = str(bounds['minlon']) + ' ' + str(bounds['maxlat'])
                geom = 'POLYGON((' + lower_left + ',' + lower_right + ',' + upper_right + ',' + upper_left + ',' + lower_left + '))'
            else:
                for member in building['members']:
                    if member['role'] == 'outer':
                        geom += build_wkt_coord_list(get_outer_way(member['ref'])['geometry'])
                geom += ')'
            cursor.execute(sql, (building['id'], building['type'],  building['tags'], geom))
        # Upload bounds if it's a multipolygon
        if building['type'] == 'multipolygon':
            bounds = building['bounds']
            lower_left = str(bounds['minlon']) + ' ' + str(bounds['minlat'])
            lower_right = str(bounds['maxlon']) + ' ' + str(bounds['minlat'])
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

problematic = []
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
    try:
        data = json.loads(data.text)
        return data['elements'][0]
    # Upload something to null island if OverpassAPI fails to return a JSON
    except ValueError:
        problematic.append(id)
        return {
                "type": "way",
                "id": id,
                "bounds": {
                "minlat": 0,
                "minlon": 0,
                "maxlat": 0,
                "maxlon": 0
                },
                "nodes": [
                ],
                "geometry": [
                    {"lat": 0, "lon": 0 },
                    {"lat": 0, "lon": 0 }
                ],
                "tags": {
                    "type": "FIXME"
                }
            }

def main():
#    print 'Calling OverpassAPI...'
#    building_data = query_buildings()
#    print 'Inserting data to Postgres db...'
#    upload_buildings(building_data)
    print 'Extracting nodes with addresses...'
    address_data = query_address()
    print 'Inserting addresses to Postgres...'
    upload_address(address_data)

if __name__ == '__main__':
    main()
