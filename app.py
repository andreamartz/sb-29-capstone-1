# import os

from flask import Flask, render_template, g, session, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import requests
from secrets import API_SECRET_KEY

API_BASE_URL = "https://www.googleapis.com/youtube/v3/search"

app = Flask(__name__)

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

    res = requests.get(
        f"{API_BASE_URL}/?part=snippet&maxResults=50&type=video&q={keyword}&key={API_SECRET_KEY}")

    data_json = res.json()
    videos = data_json['items']
    videos_data = []

    for video in data_json['items']:
        video_data = {}
        video_data["id"] = video['id']['videoId']
        video_data["title"] = video['snippet']['title']
        video_data["channelId"] = video['snippet']['channelId']
        video_data["channelTitle"] = video['snippet']['channelTitle']
        video_data["description"] = video['snippet']['description']
        video_data["thumb_url_high"] = video['snippet']['thumbnails']['high']['url']
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


@app.route("/api/get-videos", methods=["GET"])
def search_videos():
    """API endpoint.
    Get videos from YouTube based on topic entered in search field."""

    # get search form data - use a constant for now
    keyword = "web development"

    # get videos for the topic searched
    res = get_yt_videos(keyword)

    return res
