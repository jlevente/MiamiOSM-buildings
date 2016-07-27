from string import capwords

'''
Translate function used with ogr2osm for Miami-Date Large Building Footprints import.

https://github.com/jlevente/MiamiOSM-buildings

Fields used:

FIELD           DESC                    OSM_TAG
objectid        id of feature           miami_buildings:objectid
height          height of building [ft] height [m]
zip             zip code                addr:postcode
city            mailing municipality    addr:city
pre_dir         prefix of street        addr:street
suf_dir         suffix of street        addr:street
house_num       house number            addr:housenumber
st_name        name of street          addr:street
st_type        type of street          addr:street
'''

def pretty_type(type):
    types_dict = {
        "CSWY": "Causeway",
        "AVE": "Avenue",
        "ST": "Street",
        "RD": "Road",
        "TER": "Terrace",
        "PKWY": "Parkway",
        "PLZ": "Plaza",
        "LN": "Lane",
        "PSGE": "Passage",
        "TRL": "Trail",
        "PATH": "Path",
        "HWY": "Highway",
        "CIR": "Circle",
        "BLVD": "Boulevard",
        "WAY": "Way",
        "DR": "Drive",
        "EXT": "Extension",
        "PL": "Place",
        "PT": "Point",
        "CONC": "Concession",
        "PASS": "Pass",
        "CT": "Court"
    }
    return types_dict[type]

def pretty_prefix(prefix):
    prefix_dict = {
        "N": "North",
        "S": "South",
        "W": "West",
        "E": "East",
        "NW": "Northwest",
        "NE": "Northeast",
        "SW": "Southwest",
        "SE": "Southeast"
    }
    return prefix_dict[prefix]

def filterTags(attrs):
    if not attrs:
        return
    tags = {}
    
    if 'height' in attrs:
        if attrs['height'] is not None:
            # Convert feet to meters, round
            tags['height'] = unicode(round(float(attrs['height']) * 0.3048, 1))

    if 'objectid' in attrs:
        tags['miami_buildings:objectid'] = attrs['objectid']

    if 'zip' in attrs:
        if len(attrs['zip']) > 0:
            tags['addr:postcode'] = attrs['zip']

    if 'city' in attrs:
        if len(attrs['city']) > 0:
            tags['addr:city'] = capwords(attrs['city'])

    street = []

    if 'pre_dir' in attrs:
        if len(attrs['pre_dir']) > 0:
            street.append(pretty_prefix(attrs['pre_dir']))

    if 'st_name' in attrs:
        if len(attrs['st_name']) > 0:
            street.append(capwords(attrs['st_name'].lower()))

    if 'st_type' in attrs:
        if len(attrs['st_type']) > 0:
            street.append(pretty_type(attrs['st_type']))

    if 'suf_dir' in attrs:
        if len(attrs['suf_dir']) > 0:
            street.append(attrs['suf_dir'])

    street_name = ' '.join(street)
    if street_name is not '':
        tags['addr:street'] = street_name

    if 'house_num' in attrs:
        if len(attrs['house_num']) > 0:
            tags['addr:housenumber'] = attrs['house_num']

    tags['building'] = 'yes'
    #tags['source'] = 'Miami-Dade County GIS Open Data, http://gis.mdc.opendata.arcgis.com'

    return tags
