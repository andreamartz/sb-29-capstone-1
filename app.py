import os

from flask import Flask, render_template, g, session, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import requests
from models import db, connect_db, User, Course, Video, Subscription, VideoCourse
from secrets import API_SECRET_KEY

CURR_USER_KEY = "curr_user"
API_BASE_URL = "https://www.googleapis.com/youtube/v3"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///access-academy'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

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
    search_json = yt_search(keyword, MAX_RESULTS)
    items = search_json['items']

    # create list of dicts containing info & data re: individual videos
    videos_data = create_list_of_videos(items)

    # for every video in a list, call the fcn to add iframe to video
    videos_complete = get_iframes(videos_data)

    res_json = jsonify(videos_complete)

    return res_json


def yt_search(keyword, max_results):
    """Retrieve videos by keyword.
    Limit results to number in max_results.
    Return JSON response."""

    # search for video data
    res = requests.get(
        f"{API_BASE_URL}/search/?part=snippet&maxResults={max_results}&type=video&q={keyword}&key={API_SECRET_KEY}"
    )

    # turn search results into json
    res_json = res.json()

    return res_json


# create list of dicts containing info & data re: individual videos
def create_list_of_videos(items):

    videos_data = []

    for video in items:
        video_data = {}
        # add video data to video_data dict
        video_data["id"] = video['id']['videoId']
        video_data["title"] = video['snippet']['title']
        video_data["channelId"] = video['snippet']['channelId']
        video_data["channelTitle"] = video['snippet']['channelTitle']
        video_data["description"] = video['snippet']['description']
        video_data["thumb_url_high"] = video['snippet']['thumbnails']['high']['url']

        videos_data.append(video_data)

    return videos_data


# for every video returned, call the fcn to get embed iframe
def get_iframes(videos_data):
    """For every video in videos_data, add """

    for video in videos_data:
        video_id = video["id"]
        videos_json = yt_videos(video_id)
        iframe = videos_json['items'][0]['player']['embedHtml']
        video['iframe'] = iframe

    return videos_data


def yt_videos(video_id):
    """"""

    res = requests.get(
        f"{API_BASE_URL}/videos?part=player&id={video_id}&key={API_SECRET_KEY}"
    )
    videos_json = res.json()

    return videos_json

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


# ************************************
# OTHER ROUTES
# ************************************

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors by showing custom 404 page."""

    return render_template('404.html'), 404


@app.route("/")
def homepage():
    """Show homepage."""

    return render_template('home.html')


# *******************************
# USER ROUTES
# *******************************


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message and re-present form.
    """

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                image_url=form.image_url.data or User.image_url.default.arg,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


# *******************************
# VIDEO ROUTES
# *******************************


# *******************************
# COURSE ROUTES
# *******************************



@app.route("/courses/new", methods=["GET", "POST"])
def courses_add():
    """Create a new course:

    If GET: Show form. 
    If POST and form validates, add course and redirect to course edit page. 
    If form does not validate, re-present form."""

    # In this route:
    # show the form to add a course
    # try: <code to add new course>
    # except: flash a message and redirect
    # after course is created, allow user to search for videos
    # after the videos populate on the page, user can add videos to the course
    # when a video is added to the course, it will first be added to the db, then to the course
    # after the video is added to the course the video_seq will be

    # Test:
    # was a new course created successfully?
    # does the new course have the expected creator_id?
    # does the new course have the expected title?
    # does the new course have a unique title among this creator's courses?

    # CHANGE: uncomment to require login
    # if not g.user:
    #     flash("Access unauthorized.", "danger")
    #     return redirect("/")

    form = CourseAddForm()

    if form.validate_on_submit():
        # CHANGE: verify that there is not already a course with this title
        course = Course(title=form.title.data,
                        creator_id=1)

        db.session.add(course)
        db.session.commit()

        # CHANGE where this redirects to
        return redirect(f'/courses/{course.id}/edit')

    return render_template("courses/new.html", form=form)


@app.route("/courses/<int:course_id>/search-video", methods=["GET"])
def search_videos_form(course_id):
    """Display keyword search form and search results."""

    # JavaScript is handling the form submission from this page.
    # Flask API is handling the calls to YouTube Data API.

    course = Course.query.get_or_404(course_id)

    return render_template('/courses/search-video.html', course=course)


@app.route("/courses/<int:course_id>/add-video/<video_id>", methods=["POST"])
def add_video(course_id, video_id):
    """This route does not have a view.
    Add a video to database.
    Add video to a course.
    Add video sequence number within the course."""

    # get video info from hidden form fields
    id = request.form.get('v-id', None)
    title = request.form.get('v-title', None)
    description = request.form.get('v-description', None)
    channelId = request.form.get('v-channelId', None)
    channelTitle = request.form.get('v-channelTitle', None)
    thumbUrl = request.form.get('v-thumbUrl', None)
    iframe = request.form.get('v-iframe', None)

    # CHANGE: TO DO:
    # 1. Before adding a video to db, make sure it's not already been added.
    # 2.

    # create new video
    video = Video(id=id,
                  title=title,
                  description=description,
                  yt_channel_id=channelId,
                  yt_channel_title=channelTitle,
                  iframe=iframe)

    # add new video to database
    db.session.add(video)
    db.session.commit()

    # add video and sequence # to course
    # to get the sequence #, do a query to get the count of videos in the course; this will be the index of the video once it's been added
    # add the video to course, get its index in the list
    course = Course.query.get_or_404(course_id)
    video_seq = len(course.videos) + 1

    # after adding the video, check to make sure it's in videos_courses with the right sequence number

    return redirect(f'courses/{course_id}/search-video')

@app.route('/courses/<int:course_id>/edit', methods=["GET", "POST"])
def courses_edit(course_id):
    """Display a form to edit a course.
    Courses may be added, removed, or re-sequenced.
    Edit an existing course."""

    # query to get the course from the db
    # the course's videos are in course.videos
    # in the view, loop through the videos and display them

    course = Course.query.get_or_404(course_id)

    return render_template("courses/edit.html", course=course)
