from flask import Flask
from flask_heroku import Heroku
from os import environ
import logging
from openbeerplanner import ws

from flask import render_template

app = Flask(__name__)
app.debug = True# if environ.get('DEBUG') in ['True', 'true', '1'] else False
heroku = Heroku(app)
#app.config['SECRET_KEY'] = environ.get('SECRET_KEY')

#with the deveopement server we nned to serve the index.html

@app.route('/')
def root():
    return render_template('home.html')

@app.route('/list')
def list():
    amenities = ws.get_amenities()
    counters = ws.counters(amenities)
    return render_template('list.html', counters=counters)


@app.route('/fdr/<type>')
def fdr(type):
    amenities = ws.get_amenities(anemity_types=[type])
    amenities = ws.filter(amenities)
    for amenity in amenities:
        amenity.journey.build_journey(ws.Coord(lat=48.84680, lon=2.37628), amenity.coord)
        #logging.debug(amenity.journey.modes)
    return render_template('fdr.html', amenities=amenities)


@app.route('/map/<osmid>')
def map(osmid):
    amenity = ws.get_amenity(osmid)
    #logging.debug(amenity)
    amenity.journey.build_journey(ws.Coord(lat=48.84680, lon=2.37628), amenity.coord)
    return render_template('map.html', amenity=amenity)


@app.before_first_request
def setup_logging():
    logging.basicConfig(level=logging.DEBUG)
