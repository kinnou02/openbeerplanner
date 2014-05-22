from flask import Flask
from flask_restful import Api
from flask_heroku import Heroku
from os import environ
import logging

app = Flask(__name__, static_folder='static', static_url_path='')
heroku = Heroku(app)
#app.config['DEBUG'] = True if environ.get('DEBUG') in ['True', 'true', '1'] else False
#app.config['SECRET_KEY'] = environ.get('SECRET_KEY')

api = Api(app)

#with the deveopement server we nned to serve the index.html
@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.before_first_request
def setup_logging():
    #if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)
