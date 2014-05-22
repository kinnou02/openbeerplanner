import requests
import shapely.geometry as geom
import logging

__all__ = ['journeys']

URL_NAVITIA = 'https://api.navitia.io/v1/'

URL_OVERPASS = 'http://www.overpass-api.de/api/interpreter'

KM_TO_DEG = 0.0089982311916

class Coord(object):
    """
    >>> c = Coord(48.8468041, 2.370162)
    >>> str(c)
    '48.8468041;2.370162'
    """
    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat

    def __str__(self):
        return '{lon};{lat}'.format(lon=self.lon, lat=self.lat)

    def radius(self, distance=5):
        """
        >>> c = Coord(48.8468041, 2.370162)
        >>> c.radius()
        (48.83960551504672, 2.3629634150467203, 48.85400268495328, 2.37736058495328)
        """
        return geom.Point(self.lon, self.lat).buffer(distance * KM_TO_DEG).bounds

class Anemity(object):
    def __init__(self, name):
        self.name = name
        self.type = None
        self.coord = None

def journeys(self, from_, to):
    """
    run a journeys on navitia
    """
    resp = requests.get(URL + 'journeys', params={'from': from_, 'to': to})



def get_anemity(where):
    anemities = []
    anemity_types = ['cafe', 'pub', 'bar', 'restaurant', 'fast_food']
    radius = where.radius()
    param = '[out:json][timeout:25];('
    for anemity_type in anemity_types:
        param += 'node["amenity"="{anemity_type}"]{bounds};'.format(anemity_type=anemity_type, bounds=radius)
    param += ');out body;'

    resp = requests.get(URL_OVERPASS, params={'data': param})
    logging.debug('call: %s', resp.url)
    if resp.status_code != 200:
        logging.error('response KO: %s', resp.status_code)
        logging.error('response KO: %s', resp.json())

    for elem in resp.json()['elements']:
        if elem.has_key('tags') and elem['tags'].has_key('name') and elem['tags'].has_key('anemity'):
            anemity = Anemity(elem['tags']['name'])
            anemity.coord = Coord(elem['lon'], elem['lat'])
            anemity.type = elem['tags']['amenity']
            anemities.append(anemity)
    return anemities





