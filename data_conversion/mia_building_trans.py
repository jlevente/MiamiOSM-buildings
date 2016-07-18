from string import capwords

'''
Translate function used with ogr2osm for Miami-Date Large Building Footprints import.

https://github.com/jlevente/MiamiOSM-buildings

Fields used:

FIELD           DESC                    OSM_TAG
objectid        id of feature           miami_buildings:objectid
height          height of building      height
zip             zip code                addr:postcode
city            mailing municipality    addr:city
street          street                  addr:street
house_num       house number            addr:housenumber
'''

def pretty_type(type):
    types_dict = {
        "CSWY": "Causeway",
        "AVE": "Avenue",
        "ST": "Street",
        "RD": "Road",
        "TER": "Terrace",
        "PKWY": "Parkway",
        "PLZ": "",
        "LN": "",
        "PSGE": "",
        "TRL": "",
        "PATH": "Path",
        "HWY": "Highway",
        "CIR": "Circle",
        "BLVD": "Boulevard",
        "WAY": "Way",
        "DR": "Drive",
        "EXT": "Extension",
        "PL": "",
        "CONC": "",
        "PASS": "",
        "CT": "Court"
    }
    return types_dict[type]

def filterTags(attrs):
    if not attrs:
        return
    tags = {}
    
    if 'height' in attrs:
        tags['height'] = attrs['height']

    if 'objectid' in attrs:
        tags['miami_buildings:objectid'] = attrs['objectid']

    if 'zip' in attrs:
        tags['addr:postcode'] = attrs['zip']

    if 'city' in attrs:
        tags['addr:city'] = attrs['city']

    street = []

    if 'pre_dir' in attrs:
        street.append(attrs['pre_dir'])

    if 'st_name' in attrs:
        street.append(capwords(attrs['st_name'].lower()))

    if 'st_type' in attrs:
        street.append(pretty_type(attrs['st_type']))

    if 'suf_dir' in attrs:
        street.append(attrs['suf_dir'])

    street_name = ' '.join(street)
    if street_name is not '':
        tags['addr:street'] = street_name

    if 'house_num' in attrs:
        tags['addr:housenumber'] = attrs['house_num']

    tags['building'] = 'yes'
    tags['source'] = 'Miami Building Import 2016'

    return tags
