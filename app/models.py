from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Register(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    crimes = db.relationship('Crime', backref='crimes', lazy=True)
    thefts = db.relationship('Theft', backref='thefts', lazy=True)
    

class User(db.Model, UserMixin):
    idno = db.Column(db.Integer, primary_key=True, nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    phonenumber = db.Column(db.String(20), nullable=False)
    residence = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    

class Crime(db.Model, UserMixin):
    crime_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(10000), nullable=False)
    crime_location = db.Column(db.String(30), nullable=False)
    reporter_location = db.Column(db.String(30), nullable=False)
    police_station = db.Column(db.String(40), nullable=False)
    files = db.Column(db.LargeBinary)
    date_received = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    reporter = db.Column(db.Integer(), db.ForeignKey('register.id'))

class Theft(db.Model, UserMixin):
    theft_id = db.Column(db.Integer, primary_key=True)
    place_of_theft = db.Column(db.String(50), nullable=False)
    street_address = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(10), nullable=False)
    date_of_theft = db.Column(db.String(10), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    time_of_theft = db.Column(db.String(10), nullable=False)
    stolen_property = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    date_received = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    reporter = db.Column(db.Integer(), db.ForeignKey('register.id'))
