"""VideoCourse model tests."""

# run these tests like:
#
#    python -m unittest test_video_course_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy import exc
# from psycopg2 import errors

from models import db, User, Course, Video, VideoCourse

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///access-academy-test"

# Now we can import app
from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class VideoCourseModelTestCase(TestCase):
    """Test VideoCourse Model"""

    # runs before each test
    def setUp(self):
        """Add sample data.
        Create test client."""

        db.drop_all()
        db.create_all()

        user1 = User.signup("allison@allison.com", "allison", "allison", "Allison", "McAllison", None)
        user1.id = 1111

        user2 = User.signup("jackson@jackson.com", "jackson", "jackson", "Jackson", "McJackson", None)
        user2.id = 2222

        v = Video(title="Title of a YouTube Video", description="Description of a YouTube Video", yt_video_id="yfoY53QXEnI", yt_channel_id="UC29ju8bIPH5as8OGnQzwJyA")

        c = Course(title = "This course title is a test", description = "This course description is a test", creator_id = user1.id)

        db.session.add(v)
        db.session.add(c)
        db.session.commit()

        self.user1 = user1
        self.user2 = user2
        self.v = v
        self.c = c

        # set the testing client server
        self.client = app.test_client()


    # runs after each test
    def tearDown(self):
        """Remove sample data."""

        db.session.rollback()

    def test_video_course_model_functionality(self):
        """The basic VideoCourse model should work."""

        # create a video_course
        vc1 = VideoCourse(course_id=self.c.id, video_id=self.v.id, video_seq=1)

        # video_course should exist
        self.assertTrue(vc1)
        db.session.add(vc1)
        db.session.commit()

        # exactly one video_course should exist in db
        vc = VideoCourse.query.all()
        self.assertEqual(len(vc), 1)

    def test_add_dupe_video_course_fail(self):
        """An error should result if creation of a video_course is attempted with non-unique combo of course id, video id, and video seq."""

        # create a video_course
        vc1 = VideoCourse(course_id=self.c.id, video_id=self.v.id, video_seq=1)
        db.session.add(vc1)
        db.session.commit()
        self.assertEqual(vc1.course_id, 1)
        
        vc = VideoCourse.query.all()
        self.assertEqual(len(vc), 1)  

        # attempt to create another video_course that violates the composite unique constraint
        vc2 = VideoCourse(course_id=self.c.id, video_id=self.v.id, video_seq=1)
        db.session.add(vc2)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()    

        db.session.rollback()
        vc = VideoCourse.query.all()
        self.assertEqual(len(vc), 1)
  