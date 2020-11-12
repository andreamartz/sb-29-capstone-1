"""Seed database with sample data from CSV Files."""

import csv
from csv import DictReader
from app import db
from models import User, Course


db.drop_all()
db.create_all()

print('************************')

with open('generator/users.csv') as users:
    print(DictReader(users))

    db.session.bulk_insert_mappings(User, DictReader(users))

print('************************')

with open('generator/courses.csv') as courses:
    reader = csv.DictReader(courses)
    for row in reader:
        print(row)
    db.session.bulk_insert_mappings(Course, DictReader(courses))

db.session.commit()
