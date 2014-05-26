import requests
import logging
from collections import defaultdict
import random
from osmapi import OsmApi
import json
from opening_hours import OpeningHours
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

    def radius(self, distance=1):
        """
        >>> c = Coord(48.84680, 2.37628)
        >>> c.radius()
        (48.837801768808404, 2.3672817688084, 48.8557982311916, 2.3852782311916)
        """
        #disabled for heroku
        #return geom.Point(self.lon, self.lat).buffer(distance * KM_TO_DEG).bounds
        return (48.837801768808404, 2.3672817688084, 48.8557982311916, 2.3852782311916)

class Journey(object):
    def __init__(self):
        self.modes = []
        self.duration = None
        self.geojson = []

    def build_journey(self, frm, to):
        resp = requests.get(URL_NAVITIA + 'journeys', params={'from': frm, 'to': to})
        if resp.status_code == 200 and 'error' not in resp.json():
            journeys = resp.json()
            #logging.debug(journeys)
            self.duration = journeys['journeys'][0]['duration']/60
            for m in journeys['journeys'][0]['sections']:
                if 'display_informations' in m:
                    self.modes.append(m['display_informations']['commercial_mode'])
                if 'mode' in m:
                    self.modes.append(m['mode'])
                if 'geojson' in m:
                    self.geojson.append(m['geojson']['coordinates'])
                    logging.debug(self.geojson)
        else:
            logging.debug(resp.json())

class Anemity(object):
    def __init__(self, name, id):
        self.id = id
        self.name = name
        self.type = None
        self.coord = None
        self.description = None
        self.cuisine = None
        self.house_number = None
        self.street = None
        self.opening_hours = None
        self.happy_hours = None
        self.is_happy_hours = False
        self.end_happy_hours = 0
        self.phone = None
        self.brewery = []

        self.journey = Journey()

def journeys(self, from_, to):
    """
    run a journeys on navitia
    """

def counters(amenities):
    res = defaultdict(int)
    for item in amenities:
        res[item.type] += 1
    return res

def filter(amenities):
    random.shuffle(amenities)
    short_list = []
    for amenity in amenities :
        #TODO : checker tout un tas de choses (horaires ouverture, journeys duration, etc)
        short_list.append(amenity)
        if len(short_list) >=10 :
            break
    return short_list    

def get_amenities(where, anemity_types=['cafe', 'pub', 'bar', 'restaurant', 'fast_food']):
    anemities = []
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
        truc = build_amenity(elem,'tags')
        #logging.debug(truc)
        if truc :
            anemities.append(truc)
            #if truc.happy_hours :
             #   logging.debug(check_happy_hours(truc)) 
    return anemities

def check_happy_hours(chaine): 
    definition = OpeningHours(chaine)
    return definition.is_open("fr", "19:00") #ici, je fixe en dur la valeur de comparaison

def finish_happy_hours(chaine): 
    definition = OpeningHours(chaine)
    return definition.minutes_to_closing("fr", "19:00") #ici, je fixe en dur la valeur de comparaison

def get_amenity (id):
    api = OsmApi()
    dico = api.NodeGet(id)
    return build_amenity(dico, 'tag')
    
def build_amenity(elem, mon_tag ) :
        #logging.debug(elem)
        if elem.has_key(mon_tag) and elem[mon_tag].has_key('name') and elem[mon_tag].has_key('amenity'):
            anemity = Anemity(elem[mon_tag]['name'], elem['id'])
            anemity.coord = Coord(elem['lon'], elem['lat'])
            anemity.type = elem[mon_tag]['amenity']

            if elem[mon_tag].has_key('description'):
                anemity.description = elem[mon_tag]['description']

            if elem[mon_tag].has_key('cuisine'):
                anemity.cuisine = elem[mon_tag]['cuisine']

            if elem[mon_tag].has_key('addr:housenumber'):
                anemity.house_number = elem[mon_tag]['addr:housenumber']

            if elem[mon_tag].has_key('addr:street'):
                anemity.street = elem[mon_tag]['addr:street']
            if elem[mon_tag].has_key('contact:phone'):
                anemity.phone = elem[mon_tag]['contact:phone']

            if elem[mon_tag].has_key('opening_hours'):
                anemity.opening_hours = elem[mon_tag]['opening_hours']
                
            if elem[mon_tag].has_key('happy_hours'):
                anemity.happy_hours = elem[mon_tag]['happy_hours']
                anemity.is_happy_hours = check_happy_hours(anemity.happy_hours)
                anemity.end_happy_hours = finish_happy_hours(anemity.happy_hours)
                
            if elem[mon_tag].has_key('brewery'):
                anemity.brewery = elem[mon_tag]['brewery'].split(';')
                                    
            #logging.debug(anemity.happy_hours)
            return anemity
        else :
            return None
