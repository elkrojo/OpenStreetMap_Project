import xml.etree.cElementTree as ET
from collections import defaultdict
from xml_map_improve_street_names import street_type_re
from xml_map_improve_street_names import expected
from xml_map_improve_street_names import mapping
from xml_map_improve_street_names import update_name
from xml_map_improve_phone_numbers import update_phones
import pprint
import re
import csv
import codecs
import cerberus
import schema


OSM_PATH = 'dublin_city_rawdata.osm'

NODES_PATH = 'nodes.csv'
NODE_TAGS_PATH = 'nodes_tags.csv'
WAYS_PATH = 'ways.csv'
WAY_NODES_PATH = 'way_nodes.csv'
WAY_TAGS_PATH = 'way_tags.csv'

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', \
                'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, \
                    way_attr_fields=WAY_FIELDS, problem_chars=PROBLEMCHARS, \
                    default_tag_type='regular'):

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []
    count = 0

    if element.tag == 'node':
        for item in node_attr_fields:
            node_attribs[item] = element.attrib[item]

        for child in element:
            id = element.attrib['id']
            if child.tag == 'tag':
                if problem_chars.match(child.attrib['k']):
                    continue
                else:
                    tag_fields = {}
                    tag_fields['id'] = id
                    if ':' in child.attrib['k']:
                        tag_fields['type'] = child.attrib['k'].split(':', 1)[0]
                        tag_fields['key'] = child.attrib['k'].split(':', 1)[1]
                        if child.attrib['k'] == 'addr:street':
                            tag_fields['value'] = update_name(child.attrib['v'], mapping)
                        else:
                            tag_fields['value'] = child.attrib['v']

                    else:
                        tag_fields['key'] = child.attrib['k']
                        tag_fields['type'] = 'regular'
                        if child.attrib['k'] == 'phone':
                            tag_fields['value'] = update_phones(child.attrib['v'])
                        else:
                            tag_fields['value'] = child.attrib['v']

                    tags.append(tag_fields)


    elif element.tag == 'way':
        for item in way_attr_fields:
            way_attribs[item] = element.attrib[item]

        for child in element:
            id = element.attrib['id']
            if child.tag == 'nd':
                nd_fields = {}
                nd_fields['id'] = id
                nd_fields['node_id'] = child.attrib['ref']
                nd_fields['position'] = count
                count += 1
            way_nodes.append(nd_fields)

            if child.tag == 'tag':
                if problem_chars.match(child.attrib['k']):
                    continue
                else:
                    tag_fields = {}
                    tag_fields['id'] = id
                    if ':' in child.attrib['k']:
                        tag_fields['type'] = child.attrib['k'].split(':', 1)[0]
                        tag_fields['key'] = child.attrib['k'].split(':', 1)[1]
                        if child.attrib['k'] == 'addr:street':
                            tag_fields['value'] = update_name(child.attrib['v'], mapping)
                        else:
                            tag_fields['value'] = child.attrib['v']

                    else:
                        tag_fields['key'] = child.attrib['k']
                        tag_fields['type'] = 'regular'
                        if child.attrib['k'] == 'phone':
                            tag_fields['value'] = update_phones(child.attrib['v'])
                        else:
                            tag_fields['value'] = child.attrib['v']


                    tags.append(tag_fields)


    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# Secondary functions
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element dos not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# Main Function
def process_map(file_in, validate):
    """"Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
        codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
        codecs.open(WAYS_PATH, 'w') as ways_file, \
        codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
        codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

process_map(OSM_PATH, validate=True)
