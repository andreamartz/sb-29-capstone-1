"""User model tests."""

# run these tests like:
#
#    python -m unittest test_video_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy import exc

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


class UserModelTestCase(TestCase):
    """Test User Model"""

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

    ################################
    #
    # Test basic user model
    #
    ################################

    def test_user_model_functionality(self):
        """Basic user model should work"""

        u = User(username="username", email="email@email.com", password="password", first_name="Firstname", last_name="Lastname")

        db.session.add(u)
        db.session.commit()

        # User should exist and have no created courses
        self.assertTrue(u)
        self.assertEqual(len(u.courses), 0)

    ################################
    #
    # Test user signup
    #
    ################################

    def test_user_signup(self):
        """Test the signup classmethod on the User class model."""

        # create a user using signup class method
        u = User.signup("test@test.com", "testuser", "testpass", "Test", "User", None)

        uid = 99999
        u.id = uid
        db.session.add(u)
        db.session.commit()

        u = User.query.get(uid)
        self.assertIsNotNone(u)
        self.assertEqual(u.email, "test@test.com")
        self.assertNotEqual(u.password, "testpass")
        self.assertTrue(u.password.startswith("$2b$"))

    def test_signup_dupe_username(self):
        """Sign up should fail when username has already been taken."""

        invalid_u = User.signup("test@test.com", "allison", "testpass", "Test", "User", None)
        
        uid = 99999
        invalid_u.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_signup_dupe_email(self):
        """Sign up should fail when email has already been taken."""

        invalid_u = User.signup("allison@allison.com", "testuser", "testpass", "Test", "User", None)
        
        uid = 99999
        invalid_u.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_signup_missing_username(self):
        """Sign up should fail when username missing."""

        invalid_u = User.signup("test@test.com", None, "testpass", "Test", "User", None)
        
        uid = 99999
        invalid_u.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_signup_missing_email(self):
        """Sign up should fail when email is missing."""

        invalid_u = User.signup(None, "testuser", "testpass", "Test", "User", None)
        
        uid = 99999
        invalid_u.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_signup_missing_password(self):
        """Sign up should fail when password is missing."""
        with self.assertRaises(ValueError) as context:
            invalid_u = User.signup("test@test.com", "testuser", None, "Test", "User", None)

    def test_signup_missing_first_name(self):
        """Sign up should fail when first name is missing."""

        invalid_u = User.signup("test@test.com", "testuser", "testpass", None, "User", None)
        
        uid = 99999
        invalid_u.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_signup_missing_last_name(self):
        """Sign up should fail when last name ismissing."""

        invalid_u = User.signup("test@test.com", "testuser", "testpass", "Test", None, None)
        
        uid = 99999
        invalid_u.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    ################################
    #
    # Test user authentication
    #
    ################################
    def test_auth_user(self):
        """User.authenticate should successfully return a user when given a valid username & password."""

        self.assertEqual(User.authenticate("allison", "allison"), self.user1)
        self.assertEqual(User.authenticate(self.user2.username, "jackson"), self.user2)

    def test_auth_user_fail_bad_username(self):
        """User.authenticate should fail to return a user when the username is invalid."""

        self.assertFalse(User.authenticate("invalid", "allison"))

    def test_auth_user_fail_bad_password(self):
        """User.authenticate should fail to return a user when the password is invalid."""

        self.assertFalse(User.authenticate(self.user1.username, "invalid"))