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

        self.user1 = user1
        self.user2 = user2

        # Create a course
        course1 = Course(title="Jackson's Course Title", description="Jackson's Course Description", creator_id="2222")
        db.session.add(course1)
        db.session.commit()
        self.c = course1

        # Add two videos to the course
        video1 = Video(title="Video1", description="Desc for Video1", yt_video_id="yfoY53QXEnI", yt_channel_id="video1video1", yt_channel_title="Video1 Channel", thumb_url="https://i.ytimg.com/vi/yfoY53QXEnI/hqdefault.jpg")

        video2 = Video(title="Video2", description="Desc for Video2", yt_video_id="1PnVor36_40", yt_channel_id="video2video2", yt_channel_title="Video2 Channel", thumb_url="https://i.ytimg.com/vi/1PnVor36_40/hqdefault.jpg")

        db.session.add(video1)
        db.session.add(video2)
        db.session.commit()

        self.v1 = video1
        self.v2 = video2

        vc1 = VideoCourse(course_id=self.c.id, video_id=self.v1.id, video_seq=1)
        vc2 = VideoCourse(course_id=self.c.id, video_id=self.v2.id, video_seq=2)

        db.session.add(vc1)
        db.session.add(vc2)
        db.session.commit()      

        self.vc1 = vc1
        self.vc2 = vc2

        # set the testing client server
        self.client = app.test_client()

    def tearDown(self):
        """Remove sample data."""
        res = super().tearDown()
        db.session.rollback()
        return res

    # ****************************
    # Test search videos route
    # ****************************

    def test_search_videos(self):
        """A logged in course creator should be able to search for videos to add to a course he/she created."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

        # **** GET ******
        res1 = c.get("/courses/1/videos/search", follow_redirects=True)
        self.assertIn("Enter a keyword or phrase to search for videos", str(res1.data))

        # **** POST *****
        data = {"keyword": "CSS for beginners"}
        res2 = c.post("/api/get-videos", json=data)

        self.assertEqual(res2.status_code, 200)
        self.assertEqual(len(res2.json), 20)
        self.assertIn("CSS", res2.json[0]["title"])


    def test_search_videos_not_creator_fail(self):
        """A logged in user should not be able to search for videos to add to a course he/she did not create."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

        # **** GET ******
        res1 = c.get("/courses/1/videos/search", follow_redirects=True)
        self.assertIn("You must be the course creator to view this page.", str(res1.data))


    def test_search_videos_anon_fail(self):
        """An anonymous user should not be able to search for videos to add to any course."""

        with self.client as c:

            # **** GET ******
            res1 = c.get("/courses/1/videos/search", follow_redirects=True)
            self.assertIn("Access unauthorized", str(res1.data))

            # **** POST *****
            data = {"keyword": "CSS for beginners"}
            res2 = c.post("/api/get-videos", json=data, follow_redirects=True)
            # user should be redirected to the home page
            self.assertIn("What Knowledge Will You <strong>Access</strong> Today?", str(res2.data))
            self.assertIn("Access unauthorized", str(res2.data))


    # ****************************
    # Test add video to course
    # ****************************

    def test_add_video_to_course(self):
        """A logged in course creator should be able to add a video to a course he/she created."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

            res = c.post(
                "/courses/1/videos/'1Rs2ND1ryYc'/add",
                data={"v-yt-id": "1Rs2ND1ryYc", 
                "v-title": "New Video Title",
                "v-description": "New Video Description",
                "v-channelId": "New Video Channel Id",
                "v-channelTitle": "New Video Channel Title",
                "v-thumb_url": "https://i.ytimg.com/vi/1Rs2ND1ryYc/hqdefault.jpg"}, 
                follow_redirects=True)

            course = Course.query.filter(Course.creator_id == 2222).first()
            self.assertEqual(len(course.videos), 3)


    def test_add_video_to_course_not_creator_fail(self):
        """A logged in user should not be able to add a video to a course he/she did not create."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            # attempt to add a fourth video to the course
            res = c.post(
                "/courses/1/videos/'1Rs2ND1ryYc'/add",
                data={"v-yt-id": "1Rs2ND1ryYc", 
                "v-title": "New Video Title",
                "v-description": "New Video Description",
                "v-channelId": "New Video Channel Id",
                "v-channelTitle": "New Video Channel Title",
                "v-thumb_url": "https://i.ytimg.com/vi/1Rs2ND1ryYc/hqdefault.jpg"}, 
                follow_redirects=True)

            # course should contain only the three videos added by the creator
            course = Course.query.filter(Course.creator_id == 2222).first()
            self.assertEqual(len(course.videos), 2)

            # user should be redirected to the home page
            self.assertIn("What Knowledge Will You <strong>Access</strong> Today?", str(res.data))
            self.assertIn("Access unauthorized", str(res.data))


    def test_add_video_to_course_anon_fail(self):
        """An anonymous user should not be able to add a video to any course."""

        with self.client as c:

            # attempt to add a fourth video to the course
            res = c.post(
                "/courses/1/videos/'1Rs2ND1ryYc'/add",
                data={"v-yt-id": "1Rs2ND1ryYc", 
                "v-title": "New Video Title",
                "v-description": "New Video Description",
                "v-channelId": "New Video Channel Id",
                "v-channelTitle": "New Video Channel Title",
                "v-thumb_url": "https://i.ytimg.com/vi/1Rs2ND1ryYc/hqdefault.jpg"}, 
                follow_redirects=True)

            # course should contain only the three videos added by the creator
            course = Course.query.filter(Course.creator_id == 2222).first()
            self.assertEqual(len(course.videos), 2)

            # user should be redirected to the home page
            self.assertIn("What Knowledge Will You <strong>Access</strong> Today?", str(res.data))
            self.assertIn("Access unauthorized", str(res.data))