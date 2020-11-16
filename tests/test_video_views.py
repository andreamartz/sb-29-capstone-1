"""Video View tests."""

# run these tests like:
#
#    python -m unittest test_videos_views.py

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


class VideoViewTestCase(TestCase):
    """Test Video Views."""

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

        # Create a course
        course1 = Course(title="Jackson's Course Title", description="Jackson's Course Description", creator_id="2222")
        db.session.add(course1)
        db.session.commit()

        # Add three videos to the course
        video1 = Video(title="")

        self.user1 = user1
        self.user2 = user2

        # set the testing client server
        self.client = app.test_client()

    def tearDown(self):
        """Remove sample data."""
        res = super().tearDown()
        db.session.rollback()
        return res


    # ****************************
    # Test add video to db
    # ****************************

    def test_add_video_to_db(self):
        """"""

    # ****************************
    # Test search videos route
    # ****************************

    ######
    #
    # Test routes and view functions (with & w/o auth)
    #
    ######
    # Each view should return a valid response. This means:
        # The response code is what you expect and
        # Light HTML testing shows that the response is what you expect.

    # ROUTES TO TEST
    # GET /messages/new