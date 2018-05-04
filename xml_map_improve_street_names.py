
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = 'dublin_city_rawdata.osm'
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ['Street', 'Avenue', 'Boulevard', 'Drive', 'Court', 'Place', 'Square',
            'Lane', 'Road', 'Trail', 'Parkway', 'Commons', 'Centre']

mapping = { 'Center': 'Centre',
            'St': 'Street',
            'St.': 'Street',
            'Ave': 'Avenue',
            'Aveune': 'Avenue',
            'Rd': 'Road',
            'Rd.': 'Road'
            }

# takes the last word in street name, adds to dict if not expected
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

# checks for correct addr:street tag id
def is_street_name(elem):
    return (elem.attrib['k'] == 'addr:street')

# iterates osm tags and compiles dict for each unique street type
def audit(osmfile):
    osm_file = open(osmfile, 'r')
    street_types = defaultdict(set)

    for event, elem in ET.iterparse(osm_file, events=('start',)):
        if elem.tag == 'node' or elem.tag == 'way':
            for tag in elem.iter('tag'):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    osm_file.close()
    return street_types

# changes mapping keys to mapping values
def update_name(name, mapping):
    m = street_type_re.search(name)
    if m is None:
        return '-empty-'
    if m.group() not in expected:
        if m.group() in mapping.keys():
            name = re.sub(m.group(), mapping[m.group()], name)
    return name

'''
st_types = audit(OSMFILE)
pprint.pprint(dict(st_types))

for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
'''
