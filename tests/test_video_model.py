"""Video model tests."""

# run these tests like:
#
#    python -m unittest test_video_model.py


from app import app
import os
from unittest import TestCase

from models import db, User, Course, Video, Subscription, VideoCourse

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
