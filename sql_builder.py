import sqlite3
import csv
from pprint import pprint

# database file name
sqlite_file = 'dublin_city_osm.db'

# activate datbase connection
conn = sqlite3.connect(sqlite_file)

# activate cursor
cur = conn.cursor()

cur.execute('''DROP TABLE IF EXISTS nodes''')
cur.execute('''DROP TABLE IF EXISTS nodes_tags''')
cur.execute('''DROP TABLE IF EXISTS ways''')
cur.execute('''DROP TABLE IF EXISTS way_tags''')
cur.execute('''DROP TABLE IF EXISTS way_nodes''')

# commit changes
conn.commit()

# create the tables, specifying the column names and data types
cur.execute('''
    CREATE TABLE nodes(id INTEGER, lat REAL, lon REAL, user TEXT, uid INTEGER, \
                        version TEXT, changeset INTEGER, timestamp TEXT)
    ''')
cur.execute('''
    CREATE TABLE nodes_tags(id INTEGER, key TEXT, value TEXT, type TEXT)
    ''')
cur.execute('''
    CREATE TABLE ways(id INTEGER, user TEXT, uid INTEGER, version TEXT, \
                        changeset INTEGER, timestamp TEXT)
    ''')
cur.execute('''
    CREATE TABLE way_tags(id INTEGER, key TEXT, value TEXT, type TEXT)
    ''')
cur.execute('''
    CREATE TABLE way_nodes(id INTEGER, node_id INTEGER, position INTEGER)
''')

# commit the changes
conn.commit()

# read each csv file as dict, make list of tuples for each row
with open('nodes.csv', 'rb') as fin_1:
    dr_1 = csv.DictReader(fin_1)
    to_db_nodes = [(i['id'].decode('utf-8'), i['lat'].decode('utf-8'), \
                    i['lon'].decode('utf-8'), i['user'].decode('utf-8'), \
                    i['uid'].decode('utf-8'), i['version'].decode('utf-8'), \
                    i['changeset'].decode('utf-8'), \
                    i['timestamp'].decode('utf-8')) for i in dr_1]
with open('nodes_tags.csv', 'rb') as fin_2:
    dr_2 = csv.DictReader(fin_2)
    to_db_nodes_tags = [(i['id'].decode('utf-8'), i['key'].decode('utf-8'), \
                        i['value'].decode('utf-8'), \
                        i['type'].decode('utf-8')) for i in dr_2]
with open('ways.csv', 'rb') as fin_3:
    dr_3 = csv.DictReader(fin_3)
    to_db_ways = [(i['id'].decode('utf-8'), i['user'].decode('utf-8'), \
                    i['uid'].decode('utf-8'), i['version'].decode('utf-8'), \
                    i['changeset'].decode('utf-8'), \
                    i['timestamp'].decode('utf-8')) for i in dr_3]
with open('way_tags.csv', 'rb') as fin_4:
    dr_4 = csv.DictReader(fin_4)
    to_db_way_tags = [(i['id'].decode('utf-8'), i['key'].decode('utf-8'), \
                        i['value'].decode('utf-8'), \
                        i['type'].decode('utf-8')) for i in dr_4]
with open('way_nodes.csv', 'rb') as fin_5:
    dr_5 = csv.DictReader(fin_5)
    to_db_way_nodes = [(i['id'].decode('utf-8'), i['node_id'].decode('utf-8'), \
                        i['position'].decode('utf-8')) for i in dr_5]

# insert each list of tuples to the corresponding table
cur.executemany("INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, \
                timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db_nodes)
cur.executemany("INSERT INTO nodes_tags(id, key, value, type) \
                VALUES (?, ?, ?, ?);", to_db_nodes_tags)
cur.executemany("INSERT INTO ways(id, user, uid, version, changeset, timestamp) \
                VALUES (?, ?, ?, ?, ?, ?);", to_db_ways)
cur.executemany("INSERT INTO way_tags(id, key, value, type) \
                VALUES (?, ?, ?, ?);", to_db_way_tags)
cur.executemany("INSERT INTO way_nodes(id, node_id, position) \
                VALUES (?, ?, ?);", to_db_way_nodes)

# commit the changes
conn.commit()

cur.execute('SELECT * FROM nodes limit 5')
all_rows = cur.fetchall()
print('1):')
pprint(all_rows)

conn.close()
