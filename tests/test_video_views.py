"""Video View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from models import db, User, Course, Video, VideoCourse

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class VideoViewTestCase(TestCase):
    """Test views for videos."""

    def setUp(self):
        """Create test client, add sample data."""

        # drop the data
        User.query.delete()
        Video.query.delete()
        Course.query.delete()
        Video_Course.query.delete()

        # set the testing client server
        self.client = app.test_client()

        self.testuser1 = User.signup(username="testuser1",
                                    email="test@test1.com",
                                    password="testuser1",
                                    first_name="Firstname1",
                                    last_name="Lastname1",
                                    image_url=None)

        self.testuser1_id = 1111
        self.testuser1.id = self.testuser1_id

        self.testuser2 = User.signup(username="testuser2",
                                    email="test@test2.com",
                                    password="testuser2",
                                    first_name="Firstname2",
                                    last_name="Lastname2",
                                    image_url=None)

        self.testuser2_id = 2222
        self.testuser2.id = self.testuser2_id

        db.session.commit()

    def tearDown(self):
        """Remove sample data."""
        resp = super().tearDown()
        db.session.rollback()
        return resp


    # ****************************
    # TEST /videos 
    # ****************************

    # ****************************
    # TEST /videos 
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