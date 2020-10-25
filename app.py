# import os

from flask import Flask, render_template, g, session, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import requests
from secrets import API_SECRET_KEY

API_BASE_URL = "https://www.googleapis.com/youtube/v3/search"

app = Flask(__name__)

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
