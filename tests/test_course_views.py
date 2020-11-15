"""Course View Tests"""

# run these tests like:
#
#    python -m unittest test_course_views.py

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


class CourseViewsTestCase(TestCase):
    """Test Course Views"""

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


    def test_course_add(self):
        """A logged in user can view the course creation form and can create a course."""

    def test_course_add_anon_fail(self):
        """An anonymous user should not be able to view the course creation page and should be redirected to homepage."""

    def test_