from flask import Flask
from flask_heroku import Heroku
from os import environ
import logging
from openbeerplanner import ws

from flask import render_template

app = Flask(__name__, static_folder='static', static_url_path='')
app.debug = True# if environ.get('DEBUG') in ['True', 'true', '1'] else False
heroku = Heroku(app)
#app.config['SECRET_KEY'] = environ.get('SECRET_KEY')

#with the deveopement server we nned to serve the index.html

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/list')
def list():
    amenities = ws.get_amenities(ws.Coord(48.84680, 2.37628))
    amenities = ws.sort_and_filter(amenities)
    logging.debug(len(amenities))
    return render_template('list.html', amenities=amenities)


@app.route('/amenity/<id>')
def amenity(id):
    amenities = ws.get_amenities(ws.Coord(48.84680, 2.37628))
    amenities = ws.sort_and_filter(amenities)
    logging.debug(len(amenities))
    return render_template('list.html', amenities=amenities)

@app.before_first_request
def setup_logging():
    logging.basicConfig(level=logging.DEBUG)
