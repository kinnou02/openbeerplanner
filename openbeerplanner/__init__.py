from flask import Flask
from flask_restful import Api
from flask_heroku import Heroku
from os import environ
import logging
from openbeerplanner import ws

from flask import render_template

app = Flask(__name__, static_folder='static', static_url_path='')
app.debug = True# if environ.get('DEBUG') in ['True', 'true', '1'] else False
heroku = Heroku(app)
#app.config['SECRET_KEY'] = environ.get('SECRET_KEY')

api = Api(app)

#with the deveopement server we nned to serve the index.html

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/list')
def list():
    amenities = ws.get_amenity(ws.Coord(48.84680, 2.37628))
    amenities = ws.sort_and_filter(amenities)
    logging.debug(len(amenities))
    return render_template('list.html', amenities=amenities)
    #return app.send_static_file('index.html')
	
	
@app.route('/fdr/<type>')
def fdr(type):
    amenities = ws.get_amenity(ws.Coord(48.84680, 2.37628))
    amenities = ws.sort_and_filter(amenities)
    logging.debug(len(amenities))
    return render_template('fdr.html', amenities=amenities[type])
    #return app.send_static_file('index.html')

@app.before_first_request
def setup_logging():
    logging.basicConfig(level=logging.DEBUG)
