"""Course model tests."""

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
from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class CourseModelTestCase(TestCase):
    """Test Video Model"""

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

        db.session.commit()

        self.user1 = user1
        self.user2 = user2

        # set the testing client server
        self.client = app.test_client()


    # runs after each test
    def tearDown(self):
        """Remove sample data."""

        db.session.rollback()
    

    def test_course_model(self):
        """Does course model work?"""

        # create a course.
        c = Course(title = "This course title is a test", description = "This course description is a test",creator_id = self.user1.id)
        db.session.add(c)
        db.session.commit()

        # course should exist
        self.assertTrue(c)
        # course title should be: 'This course title is a test'
        self.assertEqual(self.user1.courses[0].title, "This course title is a test")
        # user1 should have one course
        self.assertEqual(len(self.user1.courses), 1)
        