import json

from flask import Flask, g
import requests

application = Flask(__name__)
application.secret_key = json.dumps('./config.json')['secret_key']

@application.before_request
def before_request():
	g.config = json.dumps('./config.json')

@application.route('/')
def home():
	return render_template('home.html')
