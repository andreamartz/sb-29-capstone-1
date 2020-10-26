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

    @classmethod
    def signup(cls, username, password, first_name, last_name):
        """Sign up user.
        Hashes password and adds user to system."""

        hashed_pw = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pw,
            first_name=first_name,
            last_name=last_name,
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
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Course(db.Model):
    """Course that is made up of videos curated by course creator"""

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(

    )

    creator_id = db.Column(

    )


class Video(db.Model):
    """Video information and data"""

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    title = db.Column(

    )

    you_tube_creator_id = db.Column(

    )


class Subscription(db.Model):
    """Join table for users and courses"""

    user_id = db.Column(

    )


class (db.Model):
    """Join table for users and courses"""
