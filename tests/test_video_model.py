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

        user1 = User.signup("allison", "allison@allison.com",
                            "allison", "http://lorempixel.com/400/400/people/1")
        user1.id = 1111

        user2 = User.signup(
            "jackson", "jackson@jackson.com", "jackson", None)
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
    

    def test_video_model(self):
        """"""



# create a video.
## video should exist
### self.assertTrue(video)






