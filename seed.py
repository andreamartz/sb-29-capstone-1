"""Seed database with sample data from CSV Files."""

import csv
from csv import DictReader
from app import db
from models import User, Course, Video, VideoCourse


db.drop_all()
db.create_all()

print('************************')

with open('generator/users.csv') as users:
    print(DictReader(users))

    db.session.bulk_insert_mappings(User, DictReader(users))

print('************************')

with open('generator/courses.csv') as courses:
    print(DictReader(courses))

    db.session.bulk_insert_mappings(Course, DictReader(courses))

print('************************')

with open('generator/videos.csv') as videos:
    print(DictReader(videos))

    db.session.bulk_insert_mappings(Video, DictReader(videos))

print('************************')

with open('generator/videos_courses.csv') as videos_courses:
    print(DictReader(videos_courses))

    db.session.bulk_insert_mappings(VideoCourse, DictReader(videos_courses))

db.session.commit()
