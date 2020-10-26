import os

from flask import Flask, render_template, g, session, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import requests
# from models import db, connect_db, User
from secrets import API_SECRET_KEY

CURR_USER_KEY = "curr_user"
API_BASE_URL = "https://www.googleapis.com/youtube/v3"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
# app.config['SQLALCHEMY_DATABASE_URI'] = (
#     os.environ.get('DATABASE_URL', 'postgres:///access-academy'))

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

# connect_db(app)

#######################################
# User signup/login/logout
#######################################


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


def get_form_data():
    """Get search data from client form."""

    # get search form data from app.js
    data = {}
    data["keyword"] = request.json['keyword']

    return data


def validate_data(data):
    """Check for missing dataa from client."""

    errors = {'errors': {}}

    # if keyword missing from form
    # CHANGE (resolve this comment and remove): I think I need this check, because otherwise an empty string would be submitted to search? Check this.
    if not data['keyword']:
        keyword_err = ["This field is required."]
        errors['errors']['keyword'] = keyword_err

    return errors


def get_yt_videos(keyword):
    """Get videos from YouTube API on a given topic."""
    MAX_RESULTS = 5

    # search for video data
    res_search = requests.get(
        f"{API_BASE_URL}/search/?part=snippet&maxResults={MAX_RESULTS}&type=video&q={keyword}&key={API_SECRET_KEY}"
    )
    # turn search results into json
    search_json = res_search.json()
    videos = search_json['items']
    videos_data = []

    for video in search_json['items']:
        video_data = {}
        # add video data to video_data dict
        video_data["id"] = video['id']['videoId']
        video_data["title"] = video['snippet']['title']
        video_data["channelId"] = video['snippet']['channelId']
        video_data["channelTitle"] = video['snippet']['channelTitle']
        video_data["description"] = video['snippet']['description']
        video_data["thumb_url_high"] = video['snippet']['thumbnails']['high']['url']

        # for each video in res_search, get the id and make a new request to the videos api url to get the embeddable iframe for the video
        # search for embeddable videos
        res_videos = requests.get(
            f"{API_BASE_URL}/videos?part=player&id={video_data['id']}&key={API_SECRET_KEY}"
        )
        videos_json = res_videos.json()

        # if retrieved video id matches the one we searched for
        if videos_json['items'][0]['id'] == video_data['id']:
            embed = videos_json['items'][0]['player']['embedHtml']
        else:
            embed = None

        video_data['embed'] = embed

        videos_data.append(video_data)

    res_json = jsonify(videos_data)

    return res_json


@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors by showing custom 404 page."""

    return render_template('404.html'), 404


@app.route("/")
def homepage():
    """Show homepage."""

    return render_template('home.html')

# *******************************
# API ENDPOINT
# *******************************


@app.route("/api/get-videos", methods=["GET", "POST"])
def search_videos():
    """API endpoint.
    Get videos from YouTube based on topic entered in search field."""

    # get search form data - use a constant for now
    data = get_form_data()
    keyword = data["keyword"]

    # do I need to check data for errors? It's only one input field, and it has the required attribute in the html.
    # validate the form data
    errors = validate_data(data)

    # if errors, return them
    if errors['errors']:
        return errors

    # no errors in data; get videos for the keyword searched
    res = get_yt_videos(keyword)

    return res

# *******************************
# USER ROUTES
# *******************************

# *******************************
# VIDEO ROUTES
# *******************************


@app.route("/videos/search", methods=["GET"])
def search_videos_form():
    """Display keyword search form and search results."""

    return render_template('/videos/search.html')

# *******************************
# COURSE ROUTES
# *******************************


@app.route("/courses/new")
def courses_add():
    """"""

    # create a new course with title (and more at this point?)
    return
