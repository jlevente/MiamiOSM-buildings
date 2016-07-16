import psycopg2
import psycopg2.extras
import requests
from osm_handler import get_outer_way

class DBHandler():
    def __init__(self, dsn):
        pg_host = 'localhost'
        pg_port = 5432
        pg_user = 'postgres'
        pg_pass = 'postgres'
        pg_db = 'osmbuildings_miami'

        # Extent of Large Building Footprints dataset
        self.bbox = '25.23561, -80.87864, 25.97467, -80.11845'
        # Downtown MIA
        self.bbox = '25.770098, -80.200582,25.780107,-80.185132'

        if dsn is not None:
            self.conn = psycopg2.connect(dsn)
        else:
            self.conn = psycopg2.connect(
                    host=pg_host,
                    port=pg_port,
                    user=pg_user,
                    password=pg_pass,
                    dbname=pg_db)
        try:
            psycopg2.extras.register_hstore(self.conn)
        except:
            print 'Could not register hstore. Are you running it for the first time? Should be OK next time.'
        self.cursor = self.conn.cursor()

    def close_db_conn(self):
        self.conn.close()

    def setup_db(self):
        create_extension_sql = '''
            CREATE EXTENSION IF NOT EXISTS postgis;
            CREATE EXTENSION IF NOT EXISTS hstore;
        '''
        create_building_table_sql = '''
            CREATE TABLE IF NOT EXISTS osm_buildings (
                id bigint,
                type varchar,
                tags hstore
            );
        -- Use generic GEOMETRY type so we can store nodes and ways together
            SELECT AddGeometryColumn('osm_buildings', 'geom', 4326, 'GEOMETRY', 2);
        '''
        create_address_table_sql = '''
            CREATE TABLE IF NOT EXISTS osm_addresses (
                id bigint,
                type varchar,
                tags hstore
            );
            SELECT AddGeometryColumn('osm_addresses', 'geom', 4326, 'POINT', 2);
        '''
        create_no_overlap_table_sql = '''
            CREATE TABLE IF NOT EXISTS buildings_no_overlap (
                objectid int PRIMARY KEY,
                source varchar,
                year_upd varchar,
                height float,
                zip float,
                city varchar,
                street varchar,
                house_num varchar
            );
            SELECT AddGeometryColumn('buildings_no_overlap','geom', 4326, 'GEOMETRY', 2);
        '''
        create_overlap_table_sql = '''
            CREATE TABLE IF NOT EXISTS buildings_overlap (
                objectid int PRIMARY KEY,
                source varchar,
                year_upd varchar,
                height float,
                zip float,
                city varchar,
                street varchar,
                house_num varchar
            );
            SELECT AddGeometryColumn('buildings_overlap','geom', 4326, 'GEOMETRY', 2);
        '''
        self.cursor.execute(create_extension_sql)
        self.cursor.execute(create_building_table_sql)
        self.cursor.execute(create_address_table_sql)
        self.cursor.execute('alter table large_buildings_2013 add column overlap boolean')
        self.conn.commit()

    def upload_address(self, data):
        sql = 'INSERT INTO osm_addresses (id, type, tags, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326));'
        for poi in data['elements']:
    #        print building
    #        print poi['type'],  poi['id']
            if poi['type'] == 'node':
                self.cursor.execute(sql, (poi['id'], poi['type'], poi['tags'], 'POINT (' + str(poi['lon']) + ' ' + str(poi['lat']) + ')'))
        self.conn.commit()

    def upload_buildings(self, data):
        with_no_geom = 0
        sql = 'INSERT INTO osm_buildings (id, type, tags, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326));'
        for building in data['elements']:
    #        print building
            print building['type'],  building['id']
            if building['type'] == 'node':
                self.cursor.execute(sql, (building['id'], building['type'], building['tags'], 'POINT (' + str(building['lon']) + ' ' + str(building['lat']) + ')'))
            # Upload them as Linestring 
            if building['type'] == 'way':
                geom = 'LINESTRING ('
                try:
                    geom += self.build_wkt_coord_list(building['geometry'])
                    geom += ')'
                    self.cursor.execute(sql, (building['id'], building['type'],  building['tags'], geom))
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
                            geom += self.build_wkt_coord_list(get_outer_way(member['ref'])['geometry'])
                    geom += ')'
                self.cursor.execute(sql, (building['id'], building['type'],  building['tags'], geom))
            # Upload bounds if it's a multipolygon
            if building['type'] == 'multipolygon':
                bounds = building['bounds']
                lower_left = str(bounds['minlon']) + ' ' + str(bounds['minlat'])
                lower_right = str(bounds['maxlon']) + ' ' + str(bounds['minlat'])
                upper_right = str(bounds['maxlon']) + ' ' + str(bounds['maxlat'])
                upper_left = str(bounds['minlon']) + ' ' + str(bounds['maxlat'])
                geom = 'POLYGON((' + lower_left + ',' + lower_right + ',' + upper_right + ',' + upper_left + ',' + lower_left + '))'
                self.cursor.execute(sql, (building['id'], building['type'],  building['tags'], geom))
        self.conn.commit()
        print '%s ways without "geometry" block' % with_no_geom

    def build_wkt_coord_list(self, geometry):
        i = 0
        coord_list = ''
        for node in geometry:
            if i > 0:
                coord_list += ', '
            coord_list += str(node['lon']) + ' ' + str(node['lat'])
            i += 1
        return coord_list

    def fix_invalid_geom(self):
        sql = '''
            UPDATE large_buildings_2013 set geom = st_makevalid(geom)
            WHERE st_isvalid(geom) is false;
        '''
        self.cursor.execute(sql)
        self.conn.commit()

    def do_intersection(self):
        self.cursor.execute('''
            update large_buildings_2013 b set overlap = true
            from osm_buildings o
            where st_intersects(b.geom, o.geom)
        ''')
        self.cursor.execute('update large_buildings_2013 set overlap = false where overlap is null')
        self.cursor.execute('''
            insert into buildings_no_overlap (objectid, source, year_upd, height, geom) (select objectid, source, year_upd, height, geom
            from
                large_buildings_2013
            where
                overlap is false)
        ''')
        self.cursor.execute('''
            insert into buildings_overlap (objectid, source, year_upd, height, geom) (select objectid, source, year_upd, height, geom
            from
                large_buildings_2013
            where
                overlap is true)
        ''')
        self.conn.commit()


    def update_address(self):
        sql = '''
            update buildings_no_overlap
            set
                zip = x.zip,
                city = x.mailing_mu,
                street = x.sname,
                house_num = x.hse_num
            from (
                select b.objectid as building_id, a.hse_num, a.sname, a.mailing_mu, a.zip, num_address.count as count_addresses
                from
                    large_buildings_2013 b,
                    address a,
                    -- Get number of addresses within each large building
                    (select building.objectid as building_id, count(a.objectid) 
                    from 
                        large_buildings_2013 building,
                        address a
                    where
                        building.geom && a.geom and
                        st_within(a.geom, building.geom)
                    group by building_id) num_address
                where
                    b.objectid = num_address.building_id and
                    num_address.count = 1 and
                    b.geom && a.geom and
                    st_within(a.geom, b.geom)
            ) x
            where
                buildings_no_overlap.objectid = x.building_id
        '''
        self.cursor.execute(sql)
        self.conn.commit()
