from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Crime(db.Model, UserMixin):
    crime_id = db.Column(db.Integer, primary_key=True)
    date_of_incident = db.Column(db.String(10), nullable=False)
    issued_by = db.Column(db.String(20), nullable=False)
    time_of_incident = db.Column(db.String(10), nullable=False)
    incident_location = db.Column(db.String(20), nullable=False)
    incident_nature = db.Column(db.String(10000), nullable=False)
    incident_details = db.Column(db.String(10000), nullable=False)
    suspect_details = db.Column(db.String(255), nullable=False)
    arrest_history = db.Column(db.String(255), nullable=False)
    suspect_name = db.Column(db.String(10))
    comments = db.Column(db.String(255))
    file_upload = db.Column(db.LargeBinary)
    date_received = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    reporter_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

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
    victim_id = db.Column(db.Integer(), db.ForeignKey('user.id'))