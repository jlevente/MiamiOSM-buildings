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
            print 'Could not register hstore. Are you running it for the first time (no hstore data in DB). You should be OK next time though.'
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
            ALTER TABLE osm_buildings ADD PRIMARY KEY (id, type);
        '''
        create_highway_railway_table_sql = '''
            CREATE TABLE IF NOT EXISTS osm_highway_railway (
                id bigint,
                type varchar,
                tags hstore
            );
        -- Use generic GEOMETRY type so we can store nodes and ways together
            SELECT AddGeometryColumn('osm_highway_railway', 'geom', 4326, 'GEOMETRY', 2);
            ALTER TABLE osm_highway_railway ADD PRIMARY KEY (id, type);
        '''
        create_address_table_sql = '''
            CREATE TABLE IF NOT EXISTS osm_addresses (
                id bigint,
                type varchar,
                tags hstore
            );
            SELECT AddGeometryColumn('osm_addresses', 'geom', 4326, 'POINT', 2);
            ALTER TABLE osm_addresses ADD PRIMARY KEY (id, type);
        '''
        create_no_overlap_table_sql = '''
            CREATE TABLE IF NOT EXISTS buildings_no_overlap (
                objectid int PRIMARY KEY,
                source varchar,
                year_upd varchar,
                height float,
                zip float,
                city varchar,
                sname varchar,
                house_num varchar,
                pre_dir varchar,
                st_name varchar,
                st_type varchar,
                suf_dir varchar
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
                sname varchar,
                house_num varchar,
                pre_dir varchar,
                st_name varchar,
                st_type varchar,
                suf_dir varchar
            );
            SELECT AddGeometryColumn('buildings_overlap','geom', 4326, 'GEOMETRY', 2);
        '''
        populate_geom_sql = 'select Populate_Geometry_Columns();'

        self.cursor.execute(create_extension_sql)
        self.cursor.execute(create_building_table_sql)
        self.cursor.execute(create_address_table_sql)
        self.cursor.execute(create_highway_railway_table_sql)
        self.cursor.execute(create_no_overlap_table_sql)
        self.cursor.execute(create_overlap_table_sql)
        self.cursor.execute(populate_geom_sql)
        self.conn.commit()

    def create_index(self):
        building_index_sql = 'CREATE INDEX osm_building_geom_idx ON osm_buildings USING GIST (geom);'
        address_index_sql = 'CREATE INDEX osm_address_geom_idx ON osm_addresses USING GIST (geom);'
        highway_index_sql = 'CREATE INDEX osm_highway_railway_geom_idx ON osm_highway_railway USING GIST (geom);'
        building_bulk_index_sql = 'CREATE INDEX osm_building_no_overlap_geom_idx ON buildings_no_overlap USING GIST (geom);'
        building_manual_index_sql = 'CREATE INDEX osm_building_overlap_geom_idx ON buildings_overlap USING GIST (geom);'
        self.cursor.execute(building_index_sql)
        self.cursor.execute(building_bulk_index_sql)
        self.cursor.execute(building_manual_index_sql)
        self.cursor.execute(address_index_sql)
        self.cursor.execute(highway_index_sql)
        self.conn.commit()

    def update_stats(self):
        old_isolation_level = self.conn.isolation_level
        self.conn.set_isolation_level(0)
        self.cursor.execute('VACUUM ANALYZE')
        self.conn.set_isolation_level(old_isolation_level)
        self.conn.commit()

    def upload_osm(self, data, table):
        i = 0
        sql_pre = 'INSERT INTO %s ' % table
        sql =  sql_pre + '(id, type, tags, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromText(%s), 4326));'
        for el in data['elements']:
            if i % 10000 == 0:
                print '%s: %s/%s' % (table, i, len(data['elements']))
            i += 1
    #        print building
    #        print el['type'],  el['id']
            if el['type'] == 'node':
                self.cursor.execute(sql, (el['id'], el['type'], el['tags'], 'POINT (' + str(el['lon']) + ' ' + str(el['lat']) + ')'))
            # Upload them as Linestring 
            if el['type'] == 'way':
                geom = 'LINESTRING ('
                try:
                    geom += self.build_wkt_coord_list(el['geometry'])
                    geom += ')'
                    self.cursor.execute(sql, (el['id'], el['type'],  el['tags'], geom))
                except KeyError:
                    continue
                    
            # Safe to assume relations are polygons but let's stick to Linestrings. Use only outer as we're interested in spatial overlaps.
            if el['type'] == 'relation':
                geom = 'LINESTRING('
                membercnt = 0
                for member in el['members']:
                    if member['role'] == 'outer':
                        membercnt += 1
                if membercnt > 1:
                    # it's already been returned if there's no bounds... passing
                    try:
                        bounds = el['bounds']
                    except KeyError:
                        continue
                    lower_left = str(bounds['minlon']) + ' ' + str(bounds['minlat'])
                    lower_right = str(bounds['maxlon']) + ' ' + str(bounds['minlat'])
                    upper_right = str(bounds['maxlon']) + ' ' + str(bounds['maxlat'])
                    upper_left = str(bounds['minlon']) + ' ' + str(bounds['maxlat'])
                    geom = 'POLYGON((' + lower_left + ',' + lower_right + ',' + upper_right + ',' + upper_left + ',' + lower_left + '))'
                else:
                    for member in el['members']:
                        if member['role'] == 'outer':
                            geom += self.build_wkt_coord_list(get_outer_way(member['ref'])['geometry'])
                    geom += ')'
                self.cursor.execute(sql, (el['id'], el['type'],  el['tags'], geom))
            # Upload bounds if it's a multipolygon
            if el['type'] == 'multipolygon':
                bounds = el['bounds']
                lower_left = str(bounds['minlon']) + ' ' + str(bounds['minlat'])
                lower_right = str(bounds['maxlon']) + ' ' + str(bounds['minlat'])
                upper_right = str(bounds['maxlon']) + ' ' + str(bounds['maxlat'])
                upper_left = str(bounds['minlon']) + ' ' + str(bounds['maxlat'])
                geom = 'POLYGON((' + lower_left + ',' + lower_right + ',' + upper_right + ',' + upper_left + ',' + lower_left + '))'
                self.cursor.execute(sql, (el['id'], el['type'],  el['tags'], geom))
        self.conn.commit()

    def build_wkt_coord_list(self, geometry):
        i = 0
        coord_list = ''
        for node in geometry:
            if i > 0:
                coord_list += ', '
            coord_list += str(node['lon']) + ' ' + str(node['lat'])
            i += 1
        return coord_list

    def move_self_intersect(self):
        sql = '''
            select array_agg(objectid) from buildings_no_overlap 
            WHERE st_isvalid(geom) is false
        '''
        self.cursor.execute(sql)
        try:
            ids_to_move = tuple(self.cursor.fetchone()[0])
        except TypeError:
            print 'No self intersecting buildings.'
            return
        # Move those buildings to the manual bucket
        insert_sql = '''
            INSERT INTO buildings_overlap (objectid, source, year_upd, height, zip, city, sname, house_num, pre_dir, st_name, st_type, suf_dir, geom) 
            (select objectid, source, year_upd, height, zip, city, sname, house_num, pre_dir, st_name, st_type, suf_dir, geom from buildings_no_overlap b
            where b.objectid IN %s)
        '''
        self.cursor.execute(insert_sql, (ids_to_move, ))
        self.conn.commit()
        # Remove buildings from bulk table
        self.cursor.execute('DELETE FROM buildings_no_overlap where objectid in %s;', (ids_to_move, ))
        print 'Moved %s buildings to manual bucket.' % len(ids_to_move)
        self.conn.commit()

    def delete_err_buildings(self):
        sql = '''
            delete from buildings_no_overlap where objectid in (
                -- ways with same position error
                35616, 64730,
                -- overlapping buildings error (area < 0.1 sq meters)
                68455);
        '''
        self.cursor.execute(sql)
        self.conn.commit()

    def do_intersection(self):
        self.cursor.execute('alter table large_buildings_2013 drop column if exists overlap;')
        self.cursor.execute('alter table large_buildings_2013 add column overlap boolean;')
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
                sname = x.sname,
                house_num = x.hse_num,
                st_name = x.st_name,
                st_type = x.st_type,
                pre_dir = x.pre_dir,
                suf_dir = x.suf_dir
            from (
                select b.objectid as building_id, a.hse_num, a.sname, a.mailing_mu, a.zip, num_address.count as count_addresses, a.pre_dir, a.suf_dir, a.st_name, a.st_type
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

    def check_and_move(self, move_type):
        if move_type == 'address':
            # Get a list of IDs of buildings close to OSM addresses
            self.cursor.execute('''
                select array_agg(b.objectid) from buildings_no_overlap b, osm_addresses a
                where
                    a.geom && b.geom and st_intersects(b.geom, a.geom) and
                    -- 30 m seems feasible. just to be safe
                    st_dwithin(b.geom::geography, a.geom::geography, 30)''')
        elif move_type == 'road/rail':
            self.cursor.execute('''
                select array_agg(b.objectid) from buildings_no_overlap b, osm_highway_railway r
                where
                    b.geom && r.geom and st_intersects(b.geom, r.geom) and (
                    (not (exist(tags, 'highway') and tags->'highway' = 'abandoned')) and
                    (not (exist(tags,'railway') and tags->'railway' = 'abandoned')) and
                    not exist(tags, 'abandoned:highway') and
                    not exist(tags, 'abandoned:railway'));''')
        else:
            print 'Wrong move_type.'
            return
        try:
            ids_to_move = tuple(self.cursor.fetchone()[0])
        except TypeError:
            print 'No buildings to move.'
            return
        # Move those buildings to the manual bucket
        insert_sql = '''
            INSERT INTO buildings_overlap (objectid, source, year_upd, height, zip, city, sname, house_num, pre_dir, st_name, st_type, suf_dir, geom) 
            (select objectid, source, year_upd, height, zip, city, sname, house_num, pre_dir, st_name, st_type, suf_dir, geom from buildings_no_overlap b
            where b.objectid IN %s)
        '''
        self.cursor.execute(insert_sql, (ids_to_move, ))
        self.conn.commit()
        # Remove buildings from bulk table
        self.cursor.execute('DELETE FROM buildings_no_overlap where objectid in %s;', (ids_to_move, ))
        print 'Moved %s buildings to manual bucket.' % len(ids_to_move)
        self.conn.commit()

    def print_report(self):
        self.cursor.execute('select count(objectid) from buildings_no_overlap')
        buildings_no_overlap = self.cursor.fetchone()[0]
        self.cursor.execute('select count(objectid) from buildings_overlap')
        buildings_overlap = self.cursor.fetchone()[0]
        self.cursor.execute('select count(objectid) from large_buildings_2013')
        large_buildings = self.cursor.fetchone()[0]
        self.cursor.execute('select count(objectid) from buildings_no_overlap where house_num is not null')
        assigned_address = self.cursor.fetchone()[0]

        text = '''
        ---------------- QUICK REPORT ----------------
        ----------------------------------------------
        Total # of buildings:                       %s
        Buildings to upload in bulk process:        %s
        Buildings in bulk process with address:     %s
        Buildings for manual inspection:            %s
        ----------------------------------------------
        '''
        print text % (large_buildings, buildings_no_overlap, assigned_address, buildings_overlap)
