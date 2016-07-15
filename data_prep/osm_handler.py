import requests
import json

class OSMHandler():
    def __init__(self):
        self.overpassAPI = 'http://overpass-api.de/api/interpreter'

        if bbox is not None:
            self.bbox = bbox
        else:
            # Downtown MIA
            self.bbox = '25.770098, -80.200582,25.780107,-80.185132'
            # Extent of Large Building Footprints dataset
            self.bbox = '25.23561, -80.87864, 25.97467, -80.11845'

    def query_buildings(self):
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

        data = requests.post(self.overpassAPI, postdata % (self.bbox))
        data = json.loads(data.text)
        return data

    def query_address():
        postdata = '''
        [out:json][bbox:%s][timeout:120];
        (
          node["addr:housenumber"];
        );
        out geom;
        out meta;
        >;
        '''

        data = requests.post(overpassAPI, postdata % (self.bbox))
        data = json.loads(data.text)
        return data

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
