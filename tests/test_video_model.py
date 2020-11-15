"""Video model tests."""

# run these tests like:
#
#    python -m unittest test_video_model.py


from app import app
import os
from unittest import TestCase

from models import db, User, Course, Video, VideoCourse

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///access-academy-test"

# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class VideoModelTestCase(TestCase):
    """Test Video Model"""

    # runs before each test
    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.signup("allison@allison.com", "allison", "allison", "Allison", "McAllison", None)
        user1.id = 1111

        user2 = User.signup("jackson@jackson.com", "jackson", "jackson", "Jackson", "McJackson", None)
        user2.id = 2222

        db.session.commit()

        self.user1 = user1
        self.user2 = user2

        # set the testing client server
        self.client = app.test_client()


    # runs after each test
    def tearDown(self):
        """Remove sample data."""

        db.session.rollback()
    

    def test_video_model_functionality(self):
        """The basic video model should work."""

        # create a video
        v = Video(title="Title of a YouTube Video", description="Description of a YouTube Video", yt_video_id="yfoY53QXEnI", yt_channel_id="UC29ju8bIPH5as8OGnQzwJyA")
        db.session.add(v)
        db.session.commit()

        # video should exist
        self.assertTrue(v)

        # video title should be correct in db
        v=Video.query.get(1)
        self.assertEqual(v.title, "Title of a YouTube Video")

        # there should be exactly one video in the db
        v=Video.query.all()
        self.assertEqual(len(v), 1)
