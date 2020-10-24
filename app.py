# import os

from flask import Flask, render_template, g, session, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import requests
from secrets import API_SECRET_KEY

API_BASE_URL = "https://www.googleapis.com/youtube/v3/search"

app = Flask(__name__)
