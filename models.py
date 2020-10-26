"""SQLAlchemy models for Capstone 1"""
# CHANGE project name above

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User of this app"""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    first_name = db.Column(
        db.Text,
        nullable=False,
    )

    last_name = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    # def __repr__(self):
    #     """Create a readable, identifiable representation of user."""
    #     return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, email, username, password, first_name, last_name, image_url):
        """Sign up user.
        Hashes password and adds user to system."""

        hashed_pw = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pw,
            first_name=first_name,
            last_name=last_name,
            image_url=image_url,
            email=email,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.hashed_pw, password)
            if is_auth:
                return user

        return False


class Course(db.Model):
    """Course that is made up of videos curated by course creator"""

    # should I keep this id?
    # if yes, how to make the id autoincrement?
    # id = db.Column(
    #     db.Integer,
    # )

    popularity = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    title = db.Column(
        db.Text,
        primary_key=True,
    )

    creator_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True,
    )


class Video(db.Model):
    """Video information and data"""

    # id comes from YouTube Data API
    id = db.Column(
        db.Text
        primary_key=True,
    )

    title = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text,
    )

    yt_channel_id = db.Column(
        db.Text,
        nullable=False,
    )

    yt_channel_title = db.Column(
        db.Text,
    )

    iframe_html = db.Column(
        db.Text,
    )

    viewCount = db.Column(
        db.Integer,
    )

    likeCount = db.Column(
        db.Integer,
    )

    pctlike = db.Column(
        db.Integer,
    )


class Subscription(db.Model):
    """Join table for users and courses"""

    subscriber_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey('courses.id', ondelete="cascade"),
        primary_key=True,
    )


class VideosCourses(db.Model):
    """Join table for videos and courses"""

    course_id = db.Column(
        db.Integer,
        db.ForeignKey('courses.id', ondelete="cascade"),
        primary_key=True,
    )

    video_id = db.Column(
        db.Text,
        db.ForeignKey('videos.id', ondelete="cascade"),
        primary_key=True,
    )

    video_seq = db.Column(
        db.Integer,
    )
