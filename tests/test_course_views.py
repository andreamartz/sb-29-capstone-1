"""Course View Tests"""

# run these tests like:
#
#    python -m unittest test_course_views.py

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


class CourseViewsTestCase(TestCase):
    """Test Course Views"""

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
        self.c_id = self.c.id

        # Add three videos to the course
        video1 = Video(title="Video1", description="Desc for Video1", yt_video_id="yfoY53QXEnI", yt_channel_id="video1video1", yt_channel_title="Video1 Channel", thumb_url="https://i.ytimg.com/vi/yfoY53QXEnI/hqdefault.jpg")

        video2 = Video(title="Video2", description="Desc for Video2", yt_video_id="1PnVor36_40", yt_channel_id="video2video2", yt_channel_title="Video2 Channel", thumb_url="https://i.ytimg.com/vi/1PnVor36_40/hqdefault.jpg")

        video3 = Video(title="Video3", description="Desc for Video3", yt_video_id="qKoajPPWpmo", yt_channel_id="video3video3", yt_channel_title="Video3 Channel", thumb_url="https://i.ytimg.com/vi/qKoajPPWpmo/hqdefault.jpg")
        db.session.add(video1)
        db.session.add(video2)
        db.session.add(video3)
        db.session.commit()

        self.v1 = video1
        self.v2 = video2
        self.v3 = video3

        vc1 = VideoCourse(course_id=self.c.id, video_id=video1.id, video_seq=1)
        vc2 = VideoCourse(course_id=self.c.id, video_id=video2.id, video_seq=2)
        vc3 = VideoCourse(course_id=self.c.id, video_id=video3.id, video_seq=3) 

        db.session.add(vc1)
        db.session.add(vc2)
        db.session.add(vc3)
        db.session.commit()      

        self.vc1 = vc1
        self.vc2 = vc2
        self.vc3 = vc3
        self.vc1_id = vc1.id
        self.vc2_id = vc2.id
        self.vc1_video_seq = self.vc1.video_seq
        self.vc2_video_seq = self.vc2.video_seq

        # set the testing client server
        self.client = app.test_client()

    def tearDown(self):
        """Remove sample data."""
        res = super().tearDown()
        db.session.rollback()
        return res


    # **********************
    # Test course add route
    # **********************

    def test_course_add(self):
        """A logged in user can view the course creation page and can create a course."""

        # mimic logging in by using the changing session trick
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            res = c.post("/courses/new", 
                        data={"title": "New Course Title", "description": "New Course Description"}, follow_redirects=True)
            
            self.assertEqual(res.status_code, 200)

            courses = Course.query.filter(Course.creator_id == 1111).all()
            self.assertEqual(len(courses), 1)
            self.assertEqual(courses[0].title, "New Course Title")
            self.assertEqual(courses[0].creator_id, 1111)
            self.assertIn('was created successfully.', str(res.data))


    def test_course_add_anon_fail(self):
        """An anonymous user should not be able to view the course creation page and should be redirected to homepage."""

        with self.client as c:
            res = c.post("/courses/new", data={"title": "New Course Title", "description": "New Course Description"}, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized", str(res.data))


    def test_course_add_dupe_fail(self):
        """A user should not be able to add a course with the same title as one of their existing courses."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            res1 = c.post("/courses/new", 
                        data={"title": "New Course Title", "description": "New Course Description"})

            # attempt to create a course with the same title by the same user
            res2 = c.post("/courses/new", 
                        data={"title": "New Course Title", "description": "Description"})

            # user is flashed a message
            self.assertIn("You have already created a course with this name. Please choose a new name.", str(res2.data))
            
            # there is exactly one course with the title "New Course Title" 
            courses = Course.query.filter(Course.title == "New Course Title", Course.creator_id == 1111).all()

            self.assertEqual(len(courses), 1)
            # self.assertEqual(len(self.user1.courses), 1)
    
    # **************************
    # Test course search route
    # **************************

    def test_course_search(self):
        """A logged in user should be able to see the courses search page and search for a course."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            # create a new course
            res1 = c.post("/courses/new", 
                        data={"title": "New Course Title", "description": "New Course Description"}, follow_redirects=True)

            # search for the new course
            res2 = c.post("/courses/search", 
                        data={"phrase": "New Course Title"}, follow_redirects=True)

            self.assertIn('Showing courses with titles matching phrases similar to New Course Title', str(res2.data))

    def test_course_search_anon_fail(self):
        """An anonymous user should not be able to access the courses search page or execute a search."""

        with self.client as c:
            res = c.post("/courses/search", data={"phrase": "Course Title"},  follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized", str(res.data))            

    def test_course_search_no_search_term(self):
        """When a logged in user executes a search for courses without providing a search term, all courses should be returned and shown."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            res = c.post("/courses/search", 
                            data={"phrase": ""})

            self.assertIn('No search term found; showing all courses', str(res.data))

    def test_course_search_no_search_match(self):
        """When a logged in user executes a search for courses and no courses match the search term, """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            # search for a course
            res = c.post("/courses/search", 
                            data={"phrase": "zzzzz"})

            self.assertIn('There are no courses with titles similar to zzzzz.', str(res.data))

    # **************************
    # Test course edit routes
    # **************************

    def test_course_edit(self):
        """A logged in course creator should be able to access the course edit page."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

            res = c.get("/courses/1/edit")
            self.assertIn("Modify a course", str(res.data))
            self.assertIn("Desc for Video1", str(res.data))
            self.assertIn("fa-arrow-down", str(res.data))
            self.assertIn("fa-arrow-up", str(res.data))
            self.assertIn("Remove</button>", str(res.data))

    def test_course_edit_404(self):
        """A logged in user who tries to access the edit page for a course number that does not exist will see custom 404 error page."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

            res = c.get("/courses/999/edit")
            self.assertIn("Sorry, this is not the page you\\\'re looking for.", str(res.data))

    def test_course_edit_not_creator_fail(self):
        """A logged in user who is NOT the course creator should NOT be able to access the course edit page."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            res = c.get("/courses/1/edit", follow_redirects=True)
            self.assertIn("You must be the course creator to view this page.", str(res.data))
            self.assertIn("What Knowledge Will You <strong>Access</strong> Today?", str(res.data))


    def test_course_edit_anon_fail(self):
        """An anonymous user should not be able to access the course edit page."""

        with self.client as c:
            res = c.get("/courses/1/edit", follow_redirects=True)

            self.assertIn("Access unauthorized", str(res.data))
            self.assertIn("What Knowledge Will You <strong>Access</strong> Today?", str(res.data))


    def test_course_remove_video(self):
        """A logged in user should be able to remove a video from a course he/she created."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id
        
            data = {"course-id": "1", "video-id": "1", "video-seq": "1"}
            res = c.post("/courses/1/videos/remove", data=data, follow_redirects=True)
            self.assertNotIn("Desc for Video1", str(res.data))


    def test_course_remove_video_not_creator_fail(self):
        """A logged in user should not be able to remove a video from a course he/she did not create."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            data = {"course-id": "1", "video-id": "1", "video-seq": "1"}
            res = c.post("/courses/1/videos/remove", data=data, follow_redirects=True)
            self.assertIn("Access unauthorized", str(res.data))
    
    # def test_course_remove_video_anon_fail(self):
        """An anonymous user should not be able to remove a video from a any course."""

        with self.client as c:

            data = {"course-id": "1", "video-id": "1", "video-seq": "1"}
            res = c.post("/courses/1/videos/remove", data=data, follow_redirects=True)
            self.assertIn("Access unauthorized", str(res.data))        

    def test_course_move_video_up(self):
        """A logged in user should be able to reorder the videos in a course he/she created."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

            data={"course-id": "1", "vc-id": "2", "video-seq": "2", "arrow": "-1"}
            res = c.post(f"courses/{self.c_id}/videos/resequence", data=data, follow_redirects=True)

            vc1 = VideoCourse.query.filter(VideoCourse.course_id == self.c_id, VideoCourse.id == self.vc1_id).all()

            vc2 = VideoCourse.query.filter(VideoCourse.course_id == self.c_id, VideoCourse.id == self.vc2_id).all()

            self.assertEqual(vc1[0].video_seq, 2)
            self.assertEqual(vc2[0].video_seq, 1)

    def test_course_move_video_up_not_creator_fail(self):
        """A logged in user should not be able to reorder the videos in a course he/she did not create."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            data = {"course-id": "1", "video-id": "2", "video-seq": "2", "arrow": "-1"}
            res = c.post(f"/courses/{self.c_id}/videos/resequence", data=data, follow_redirects=True)

            self.assertIn("Access unauthorized", str(res.data))


    def test_course_move_video_up_anon_fail(self):
        """An anonymous user should not be able to reorder the videos in any course."""

        with self.client as c:
            data={"course-id": "1", "vc-id": "2", "video-seq": "2", "arrow": "-1"}
            res = c.post(f"courses/{self.c.id}/videos/resequence", data=data, follow_redirects=True)

            self.assertIn("Access unauthorized", str(res.data))

    def test_course_edit_move_video_down(self):
        """A logged in user should be able to reorder the videos in a course he/she created."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

            data={"course-id": "1", "vc-id": "1", "video-seq": "1", "arrow": "1"}
            res = c.post(f"courses/{self.c_id}/videos/resequence", data=data, follow_redirects=True)

            vc1 = VideoCourse.query.filter(VideoCourse.course_id == self.c_id, VideoCourse.id == self.vc1_id).all()

            vc2 = VideoCourse.query.filter(VideoCourse.course_id == self.c_id, VideoCourse.id == self.vc2_id).all()

            self.assertEqual(vc1[0].video_seq, 2)
            self.assertEqual(vc2[0].video_seq, 1)

    # def test_course_move_video_down_not_creator_fail(self):
    #     """A logged in user should not be able to reorder the videos in a course he/she did not create."""

    def test_course_move_video_down_anon_fail(self):
        """An anonymous user should not be able to reorder the videos in any course."""

        with self.client as c:
            data={"course-id": "1", "vc-id": "1", "video-seq": "1", "arrow": "1"}
            res = c.post(f"courses/{self.c.id}/videos/resequence", data=data, follow_redirects=True)

            self.assertIn("Access unauthorized", str(res.data))

    # ***************************
    # Test course details route
    # ***************************

    def test_course_details(self):
        """A logged in user should be able to view the videos that are part of a course."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id    

            res = c.get("/courses/1/details")
            self.assertIn("View videos in course", str(res.data))

    def test_course_details_anon_fail(self):
        """An anonymous user should not be able to view the course details page."""

        with self.client as c:
            res = c.get("/courses/1/details", follow_redirects=True)
            self.assertIn("Access unauthorized", str(res.data))