#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# 
import requests
import logging
import datetime
import calendar
from collections import defaultdict
import random
from osmapi import OsmApi
import json
from opening_hours import OpeningHours
__all__ = ['journeys']

URL_NAVITIA = 'https://beta.navitia.io/v1/'
#URL_NAVITIA = 'https://api.navitia.io/v1/'

API_key = "7b9c9e1a-0644-438b-8705-91bd86f0fb13"

URL_OVERPASS = 'http://www.overpass-api.de/api/interpreter'

bouchon = False #option de bouchonage pour les horaires d'ouvertures en cas de démo à une heure pourrie

donuts = [(["GrandCercle", 400], ["PetitCercle", 0]),
          (["GrandCercle", 750], ["PetitCercle", 400]),
          (["GrandCercle", 1300], ["PetitCercle", 750])]

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

class Journey(object):
    def __init__(self):
        self.modes = []
        self.duration = None
        self.arrivaldatetime_OSM = None
        self.geojson = []

    def build_journey(self, frm, to):
        resp = requests.get(URL_NAVITIA + 'journeys', params={'from': frm, 'to': to} , headers={'Authorization': API_key})
        #TODO : je crois qu'il faut passer une date aussi ... y a du 13h37 dans l'air là !
        if resp.status_code == 200 and 'error' not in resp.json():
            journeys = resp.json()
            self.duration = journeys['journeys'][0]['duration']/60
            arrivaldatetime = journeys['journeys'][0]['arrival_date_time']
            date_object = datetime.datetime.strptime(arrivaldatetime, '%Y%m%dT%H%M%S')
            self.arrivaldatetime_OSM = (calendar.day_name[calendar.weekday(date_object.year, date_object.month, date_object.day)][0:2] ,"%d:%d" % (date_object.hour,date_object.minute) )
            #logging.debug(self.arrivaldatetime_OSM)
            for m in journeys['journeys'][0]['sections']:
                if 'display_informations' in m:
                    self.modes.append(m['display_informations']['commercial_mode'])
                if 'mode' in m:
                    self.modes.append(m['mode'])
                if 'geojson' in m:
                    self.geojson.append(m['geojson']['coordinates'])
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

def check_amenity(my_amenity):
    my_amenity.journey.build_journey(Coord(lat=48.84680, lon=2.37628), my_amenity.coord)
  
    #remplissage des infos sur les happy hours
    if my_amenity.happy_hours :
        my_amenity.is_happy_hours = check_happy_hours(my_amenity.happy_hours, my_amenity.journey.arrivaldatetime_OSM )
        my_amenity.end_happy_hours = finish_happy_hours(my_amenity.happy_hours, my_amenity.journey.arrivaldatetime_OSM)
                           
    #TODO : checker tout un tas de choses (horaires ouverture, journeys duration, etc)
    return True

def filter(amenities):
    random.shuffle(amenities)
    short_list = []
    for amenity in amenities :
        if check_amenity(amenity):
            short_list.append(amenity)
        if len(short_list) >=10 :
            break
    return short_list

def get_amenities(anemity_types=['cafe', 'pub', 'bar', 'restaurant', 'fast_food'], mood=2):
    anemities = []
    param = """ <osm-script output="json"> """
    for atype in anemity_types :
        for cercle in donuts[mood-1]:
            param += """<query type="node">
        <id-query ref="1376730447" type="node"/>
        </query>"""

            param += """<query type="node" into='"""+cercle[0] +"""'>
            <around radius='"""+str(cercle[1])+"""'/>
            <has-kv k="amenity" v='"""+atype +"""'/>
            </query>"""


        param += """
          <difference into="_">
            <query into="_" type="node">
              <item set="GrandCercle"/>
            </query>
            <query into="_" type="node">
              <item set="PetitCercle"/>
            </query>
          </difference>
          <print/>


            """
    param += ' </osm-script>'

    resp = requests.get(URL_OVERPASS, params={'data': param})
    #logging.debug('call: %s', resp.url)
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

def check_happy_hours(chaine, jour_heure):
    definition = OpeningHours(chaine)
    if bouchon :
    	return definition.is_open("fr", "19:00")
    return definition.is_open(jour_heure[0], jour_heure[1])
    

def finish_happy_hours(chaine, jour_heure):
    definition = OpeningHours(chaine)
    if bouchon :
    	return definition.minutes_to_closing("fr", "19:00") 
    return definition.minutes_to_closing(jour_heure[0], jour_heure[1])

def get_amenity (id):
    api = OsmApi()
    dico = api.NodeGet(id)
    return build_amenity(dico, 'tag')

def build_amenity(elem, mon_tag ) :
    #logging.debug(elem)
    traduction = { 
        "regional": u"régionale",
        "japanese": u"japonaise",
        "italian": u"italienne",
        "french" : u"française",
        "senegalese" : u"sénégalaise",
        "asian" : u"asiatique",
        "korean" : u"coréenne",
        "indian" : u"indienne",
        "argentinian" : u"argentine",
        "chinese" : u"chinoise",
        "brasilian" : u"brésilienne",
        "mexican" : u"mexicaine",
        "coffe_shop" : u"café",
        "indonesian" : u"indonésienne",
        "arab" : u"arabe",
        "libanese" : u"libanaise",
        "fish" : u"à base de poisson",
        "seafood": u'à base de poisson',
        "american" : u"américaine",
        "polonese" : u"polonaise",
        "caribbean" : u"des Caraïbes",
        "ivoirian" : u"ivoirienne",
        "vietnamese" : u"vietnamienne",
        "ethiopan" : u"éthiopienne",
        "chinese" : u"chinoise",
        "spanish" : u"espagnole",
        "jewish" : u"juive",
        "russian" : u"russe",
        "marocan" : u"marocaine",
        "cake" : u"gateaux",
        "vegetarian" : u"végétarienne",
        "peruvian" : u"péruvienne",
        "gastronomic" : u"gastronomique",
        "maltese" : u"de Malte",
        "ice_cream" : u"glaces",
        "tibetan" : u"du Tibet",
        "berber" : u"berbère",
        "latin_american" : u"d'Amérique Latine",
        "greek" : u"grecque",
        "african" : u"africaine"
    }
    if elem.has_key(mon_tag) and elem[mon_tag].has_key('name')\
            and elem[mon_tag].has_key('amenity'):
        anemity = Anemity(elem[mon_tag]['name'], elem['id'])
        anemity.coord = Coord(elem['lon'], elem['lat'])
        anemity.type = elem[mon_tag]['amenity']

        if elem[mon_tag].has_key('description'):
            anemity.description = elem[mon_tag]['description']

        if elem[mon_tag].has_key('cuisine'):
            if elem[mon_tag]['cuisine'] in traduction :
                anemity.cuisine = traduction[elem[mon_tag]['cuisine']]
            else :
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

        if elem[mon_tag].has_key('brewery'):
            anemity.brewery = elem[mon_tag]['brewery'].split(';')

        #logging.debug(anemity.happy_hours)
        return anemity
    else :
        return None
