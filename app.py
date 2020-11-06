import os

from flask import Flask, render_template, g, session, request, jsonify, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests

from forms import UserAddForm, LoginForm, CourseAddForm

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


# CHANGE: take this line out after authentication is added in:
# session[CURR_USER_KEY] = 1


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


# ************************************
# HELPER FUNCTIONS - login/logout
# ************************************

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

# ************************************************
#
# HELPER FUNCTIONS - Flask API search for videos
#
# ************************************************

# TO DO:
# 1. get likeCount and viewCount for each video from YT
# 2.


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

    MAX_RESULTS = 20

    # search for video data
    search_json = yt_search(keyword, MAX_RESULTS)
    items = search_json['items']

    # create list of dicts containing info & data re: individual videos
    videos_data = create_list_of_videos(items)

    # CHANGE: for now do not call the YT API to get the embeddable iframes; uncomment this after development mostly done
    # for every video in a list, call the fcn to add iframe to video
    # videos_complete = get_iframes(videos_data)
    # res_json = jsonify(videos_complete)

    # CHANGE: when switching to rendering videos, remove this line
    res_json = jsonify(videos_data)

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
        video_data["ytVideoId"] = video['id']['videoId']
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
        yt_video_id = video["ytVideoId"]
        videos_json = yt_videos(yt_video_id)
        iframe = videos_json['items'][0]['player']['embedHtml']
        video['iframe'] = iframe

    return videos_data


def yt_videos(yt_video_id):
    """Make API call to YouTube Data API.
    Return the result in JSON format."""

    res = requests.get(
        f"{API_BASE_URL}/videos?part=player&id={video_id}&key={API_SECRET_KEY}"
    )
    videos_json = res.json()

    return videos_json


# *******************************
# API ENDPOINT ROUTE
# *******************************

@app.route("/api/get-videos", methods=["GET", "POST"])
def search_videos():
    """API endpoint.
    Get videos from YouTube based on topic entered in search field."""

    # get search form data
    data = get_form_data()
    keyword = data["keyword"]

    # CHANGE: delete comment below
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
    """Show homepage.

    - anon users: no courses
    - logged in: courses created
    """
    if g.user:
        # query for the courses by this creator
        courses = (Course
                   .query
                   .filter(Course.creator_id == g.user)
                   .order_by(Course.title.asc())
                   .all())
        return render_template('home.html', courses=courses)
    else:
        return render_template('home-anon.html')


# *******************************
# USER ROUTES
# *******************************

# TO DO:
# 1. get likeCount and viewCount for each video from YT
# 2. create route to delete a user - need ????
# 3. create route to view user's created courses
# 4. create route to view user's subscribed courses


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

# TO DO:
# 1. Before adding a course to db, make sure there's not already a course by that name for that creator.
# 2. Before adding a course to db, make sure the videos have been added and sequenced.
# 3. Prevent subscriptions to a course if the creator is the logged in user?
# 4. Create a route for non-creators to view the course details, such as the videos in a course.
# 5. Create a route for creators to view and edit the course details, such as removing a video and re-ordering videos.


@app.route("/courses/new", methods=["GET", "POST"])
def courses_add():
    """Create a new course:

    If GET: Show the course add form. 
    If POST and form validates: 
        * course title does not exist yet for this creator: add course and redirect to course edit page
        * course does exist already for this creator:
    If POST and form does not validate, re-present form."""

    # In this route:
    # try: <code to add new course>
    # except: flash a message and redirect
    # after course is created, allow user to search for videos

    # CHANGE: uncomment to require login
    # if not g.user:
    #     flash("Access unauthorized.", "danger")
    #     return redirect("/")

    form = CourseAddForm()

    if form.validate_on_submit():
        # CHANGE: after login func added, stop hard-coding the creator_id
        # check to see if course already exists for this creator
        course = Course.query.filter(
            Course.title == form.title.data, Course.creator_id == 1).first()

        if course:
            flash("You have already created a course with this name.", "warning")

        else:

            # CHANGE: after login functionality added, stop hard-coding the creator_id
            course = Course(title=form.title.data,
                            creator_id=1)

            db.session.add(course)
            db.session.commit()

            flash(
                f'Your course "{course.title}" was created successfully.', 'success')

            # CHANGE where this redirects to
            return redirect(f'/courses/{course.id}/search-video')

    return render_template("courses/new.html", form=form)


@app.route("/courses/<int:course_id>/search-video", methods=["GET"])
def search_videos_form(course_id):
    """Display keyword search form and search results."""

    # JavaScript is handling the form submission from this page.
    # Flask API is handling the calls to YouTube Data API.

    course = Course.query.get_or_404(course_id)

    # CHANGE: Right now, the videos searched disappear after a video is added to the course...
    # CHANGE: ...When the user comes back to the search page, they have to start the search again.
    # CHANGE: ...Is it easy to fix this or is this a V.2 feature?

    return render_template('/courses/search-video.html', course=course)


@app.route("/courses/<int:course_id>/add-video/<yt_video_id>", methods=["POST"])
def add_video_to_course(course_id, yt_video_id):
    """This route does not have a view.
    Check to see if the video is in the database already.
    If not, add the video to database.
    Check to see if the video is part of the course already.
    If not, add the video to the course.
    Add video sequence number within the course."""

    # create video & add to db if not already there
    form_data = request.form
    video = add_video_to_db(form_data, yt_video_id)

    # Query the db for this course
    course = Course.query.get_or_404(course_id)

    # CHANGE: currently, if video is already part of course, redirect back to search page. this should be changed so that the "Add to course" button is deactivated (or the video isn't even displayed on the search page) if the video is already part of the course, so that the user never gets here.
    # is the video already part of the course?
    if video in course.videos:
        flash("This video has already been added to the course.", "warning")
        return redirect(f'../../../courses/{course_id}/search-video')

    video_seq = len(course.videos) + 1

    # CHANGE: QUESTION: is this the best way to add a value to a join table???
    video_course = VideoCourse(course_id=course_id,
                               video_id=video.id,
                               video_seq=video_seq)

    db.session.add(video_course)
    db.session.commit()

    flash("Good news! The video was successfully added to the course.", "success")

    # CHANGE: why do I need all of the dots and slashes here, but not in other routes?
    return redirect(f'../../../courses/{course_id}/search-video')

# CHANGE: is this the best route name (/courses/<int:course_id>/edit')? should 'edit' come before the course_id? why?


@app.route('/courses/<int:course_id>/edit', methods=["GET", "POST"])
def courses_edit(course_id):
    """Display the videos in the course.
    Courses may be added, removed, or re-sequenced.
    Edit an existing course."""

    # include a button ("Add a video") that takes the user to the '/courses/<int:course_id>/add-video/<video_id' route
    # query to get the course from the db
    # the course's videos are in course.videos
    # in the view, loop through the videos and display them IN THE CORRECT ORDER for the course

    # CHANGE: QUESTION: is using a join table like this a proper way/ a good way to get the ordered videos
    # CHANGE: QUESTION: should I pull the videos themselves or just a list of the sequence numbers?
    course = Course.query.get_or_404(course_id)
    # videos_courses = course.videos_courses

    videos_courses_asc = (VideoCourse
                          .query
                          .filter(VideoCourse.course_id == course_id)
                          .order_by(VideoCourse.video_seq)
                          .all())

    return render_template("courses/edit.html", course=course, videos_courses=videos_courses_asc)


@app.route('/courses/<int:course_id>/re-sequence', methods=["POST"])
def courses_resequence(course_id):
    """There is no view for this route.
    Resequence the videos within a course.
    """

    # Query to get the course
    course = Course.query.get_or_404(course_id)

    # get the video data from the form
    video_id = request.form.get('video-id')
    vc_id = request.form.get('vc-id')
    video_seq = int(request.form.get('video-seq'))

    arrow = request.form.get('arrow')
    arrow = int(arrow)

    # CHANGE: vc and vc_switch should always have length one; what's the best way to rewrite this? .first()?
    vc = VideoCourse.query.filter(
        VideoCourse.id == vc_id
    ).all()

    vc_switch = VideoCourse.query.filter(
        VideoCourse.course_id == course_id,
        VideoCourse.video_seq == (video_seq + arrow)
    ).all()

    # update with new video_course_video_seq
    temp_seq = -1
    # curr_seq = video_seq
    vc[0].video_seq = temp_seq
    vc_switch[0].video_seq = video_seq
    vc[0].video_seq = video_seq + arrow

    db.session.commit()

    # re-render the course edit page

    return redirect(f'../../courses/{course_id}/edit')


@app.route('/courses/<int:course_id>/remove-video', methods=["POST"])
def remove_video(course_id):
    """There is no view for this route.
    Remove a video from a course.
    If the video is only part of one course, also remove video from db.
    """

    # CHANGE: add to docstring if will also be re-sequencing the videos within the course

    # Query to get the course
    course = Course.query.get_or_404(course_id)
    # get the video_id from the form
    # CHANGE: should this be instead request.form.get('video-id', None)?
    # potential advantage is to avoid an error?
    video_id = request.form.get('video-id')

    # get the video sequence number from the form
    video_seq = int(request.form.get('video-seq'))

    videos_courses = VideoCourse.query.filter(
        VideoCourse.video_id == video_id).all()

    # if no other courses use this video, remove the video from the db (the delete will cascade to the videos_courses table)
    if len(videos_courses) == 1:
        Video.query.filter(Video.id == video_id).delete()
        db.session.commit()

    # otherwise leave video in the db and remove the corresponding entry from videos_courses table only
    else:
        VideoCourse.query.filter(
            VideoCourse.course_id == course.id,
            VideoCourse.video_id == video_id
        ).delete()
        db.session.commit()

    # resequence the remaining videos in the course - necessary? YES! to make re-sequencing arrows work properly
    vc_reorder = VideoCourse.query.filter(
        VideoCourse.course_id == course.id,
        VideoCourse.video_seq > video_seq
    )

    for vc in vc_reorder:
        vc.video_seq = vc.video_seq - 1

    # re-render the course edit page without the removed video

    return redirect(f'../../courses/{course_id}/edit')

# *********************************
#
# COURSE ROUTES HELPER FUNCTIONS
#
# *********************************


def add_video_to_db(form_data, yt_video_id):
    """Add a video to the database."""

    # CHANGE: should .first() be .one_or_none instead?
    video = Video.query.filter(Video.yt_video_id == yt_video_id).first()

    if not video:
        # CHANGE: is there a more efficient way to do this?
        # get video info from hidden form fields
        # CHANGE: pull this out into a helper function
        title = form_data.get('v-title', None)
        description = form_data.get('v-description', None)
        channelId = form_data.get('v-channelId', None)
        channelTitle = form_data.get('v-channelTitle', None)
        thumbUrl = form_data.get('v-thumbUrl', None)
        iframe = form_data.get('v-iframe', None)

        # create new video
        # CHANGE: pull this out into a helper function
        video = Video(title=title,
                      description=description,
                      yt_video_id=yt_video_id,
                      yt_channel_id=channelId,
                      yt_channel_title=channelTitle,
                      thumbUrl=thumbUrl,
                      iframe=iframe)

        # add new video to database
        db.session.add(video)
        db.session.commit()

    return video
