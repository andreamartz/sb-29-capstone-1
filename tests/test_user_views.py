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

        db.session.commit()

        self.user1 = user1

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

            username = data["username"]
            res = c.post(
            "/signup", data=data, follow_redirects=True)

            self.assertIn(f"Welcome {username}!", str(res.data))

    def test_user_signup_dupe_username_fail(self):
        """A user should not be able to register an account with a username that has already been taken. After doing so, the user will be logged in."""

        with self.client as c:
            data={"username": "allison",
            "password": "Password",
            "first_name": "FirstName",
            "last_name": "LastName",
            "image_url": None,
            "email": "email@email.com"}

            res = c.post(
            "/signup", data=data, follow_redirects=True)

            self.assertIn("Username or email already taken", str(res.data))

    def test_user_signup_dupe_email_fail(self):
        """A user should not be able to register an account with an email that has already been taken."""

        with self.client as c:
            data={"username": "UserName",
            "password": "Password",
            "first_name": "FirstName",
            "last_name": "LastName",
            "image_url": None,
            "email": "allison@allison.com"}

            res = c.post(
            "/signup", data=data, follow_redirects=True)

            self.assertIn("Username or email already taken", str(res.data))

    def test_user_login(self):
        """A registered user should be able to login."""

        with self.client as c:
            data={"username": "allison",
            "password": "allison"}

            username = data["username"]
            res = c.post("/login", data=data, follow_redirects=True)

            self.assertIn("Hello,", str(res.data))

    def test_user_logout(self):
        """When a logged in user clicks logout, their id should be removed from the session."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            res = c.get("/logout", follow_redirects=True)

            self.assertIn("Welcome back.</p>", str(res.data))
            self.assertIn("Log in</button>", str(res.data))