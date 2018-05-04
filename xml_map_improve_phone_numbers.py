
import xml.etree.cElementTree as ET

OSMFILE = 'dublin_city_rawdata.osm'

# add phone tag value to set
def audit_phone_type(phone_types, phone_name):
    phone_types.add(phone_name)

# checks for correct tag key
def is_phone_number(elem):
    return (elem.attrib['k'] == 'phone')

# iterates osm tags and makes set of phone numbers
def audit_phone(osmfile):
    osm_file = open(osmfile, 'r')
    phone_types = set()
    for event, elem in ET.iterparse(osm_file, events=('start',)):
        if elem.tag == 'node' or elem.tag == 'way':
            for tag in elem.iter('tag'):
                if is_phone_number(tag):
                    audit_phone_type(phone_types, tag.attrib['v'])
    osm_file.close()
    return phone_types

# reformats digits for locality
def update_phones(phonenumber):

# remove all symbols from number
    phonenumber = ''.join(ele for ele in phonenumber if ele.isdigit())

    if phonenumber is None:
        return '-empty-'

# eliminate country codes from beginning of number, add zero for area code
    if phonenumber.startswith('3530'):
        phonenumber = '0' + phonenumber[4:]
    elif phonenumber.startswith('353'):
        phonenumber = '0' + phonenumber[3:]
    elif phonenumber.startswith('00353'):
        phonenumber = '0' + phonenumber[5:]

# reshape landlines to common digit spacing format for locality
    if len(phonenumber) == 9:
        phonenumber = ('({0}) {1} {2}'.format(phonenumber[:2], phonenumber[2:5]\
        , phonenumber[5:]))

# reshape mobiles to common digit spacing format for locality
    elif len(phonenumber) == 10 and phonenumber.startswith('08'):
        phonenumber = ('({0}) {1} {2}'.format(phonenumber[:3], phonenumber[3:6]\
        , phonenumber[6:]))


    return phonenumber

'''
ph_list = audit_phone(OSMFILE)

for phone_number in ph_list:
    print phone_number, '==>',
    phone_number = update_phones(phone_number)
    print phone_number
'''
