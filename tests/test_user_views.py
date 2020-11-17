"""User View Tests"""

# run these tests like:
#
#    python -m unittest test_user_views.py

import os
from unittest import TestCase
from models import db, User, Course, Video, VideoCourse

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///access-academy-test"

# Now we can import app
from app import app, CURR_USER_KEY

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewsTestCase(TestCase):
    """Test User Views"""

    def setUp(self):
        """Add sample data.
        Create test client."""

        # drop the database tables and recreate them
        db.drop_all()
        db.create_all()

        user1 = User.signup("allison@allison.com", "allison", "allison", "Allison", "McAllison", None)
        user1.id = 1111

        user2 = User.signup("jackson@jackson.com", "jackson", "jackson", "Jackson", "McJackson", None)
        user2.id = 2222

        db.session.commit()

        self.user1 = user1
        self.user2 = user2

        # # Create a course
        # course1 = Course(title="Jackson's Course Title", description="Jackson's Course Description", creator_id="2222")
        # db.session.add(course1)
        # db.session.commit()
        # self.c = course1

        # # Add three videos to the course
        # video1 = Video(title="Video1", description="Desc for Video1", yt_video_id="yfoY53QXEnI", yt_channel_id="video1video1", yt_channel_title="Video1 Channel", thumb_url="https://i.ytimg.com/vi/yfoY53QXEnI/hqdefault.jpg")

        # video2 = Video(title="Video2", description="Desc for Video2", yt_video_id="1PnVor36_40", yt_channel_id="video2video2", yt_channel_title="Video2 Channel", thumb_url="https://i.ytimg.com/vi/1PnVor36_40/hqdefault.jpg")

        # video3 = Video(title="Video3", description="Desc for Video3", yt_video_id="qKoajPPWpmo", yt_channel_id="video3video3", yt_channel_title="Video3 Channel", thumb_url="https://i.ytimg.com/vi/qKoajPPWpmo/hqdefault.jpg")
        # db.session.add(video1)
        # db.session.add(video2)
        # db.session.add(video3)
        # db.session.commit()

        # self.v1 = video1
        # self.v2 = video2
        # self.v3 = video3

        # vc1 = VideoCourse(course_id=self.c.id, video_id=video1.id, video_seq=1)
        # vc2 = VideoCourse(course_id=self.c.id, video_id=video2.id, video_seq=2)
        # vc3 = VideoCourse(course_id=self.c.id, video_id=video3.id, video_seq=3) 

        # db.session.add(vc1)
        # db.session.add(vc2)
        # db.session.add(vc3)
        # db.session.commit()      

        # self.vc1 = vc1
        # self.vc2 = vc2
        # self.vc3 = vc3

        # set the testing client server
        self.client = app.test_client()

    def tearDown(self):
        """Remove sample data."""
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_signup(self):
        """A user should be able to register an account with a unique username. After doing so, the user will be logged in."""

        with self.client as c:
            data={"username": "UserName",
            "password": "Password",
            "first_name": "FirstName",
            "last_name": "LastName",
            "image_url": None,
            "email": "email@email.com"}
            # "https://i.ytimg.com/vi/1Rs2ND1ryYc/hqdefault.jpg"

            res = c.post(
            "/courses/1/videos/'1Rs2ND1ryYc'/add", data=data,
            follow_redirects=True)

            # self.assert

    # def test_user_signup_dupe_username_fail(self):
    #     """A user should not be able to register an account with a username that has already been taken. After doing so, the user will be logged in."""

    # def test_user_login(self):
    #     """A registered user should be able to login."""

    # def test_user_logout(self):
    #     """When a logged in user clicks logout, their id should be removed from the session."""

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.user1.id