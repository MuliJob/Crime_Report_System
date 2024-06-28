from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Crime(db.Model, UserMixin):
    crime_id = db.Column(db.Integer, primary_key=True)
    date_of_incident = db.Column(db.String(10), nullable=False)
    issued_by = db.Column(db.String(20), nullable=True)
    time_of_incident = db.Column(db.String(10), nullable=False)
    incident_location = db.Column(db.Text, nullable=False)
    incident_nature = db.Column(db.Text, nullable=False)
    incident_details = db.Column(db.Text, nullable=False)
    suspect_details = db.Column(db.Text, nullable=True)
    arrest_history = db.Column(db.Text, nullable=False)
    suspect_name = db.Column(db.String(10), nullable=True)
    comments = db.Column(db.Text, nullable=True)
    crime_status = db.Column(db.String(10), nullable=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    crime_file_upload = db.Column(db.Text, nullable=True)
    crime_file_name = db.Column(db.Text, nullable=True)
    crime_mimetype = db.Column(db.Text, nullable=True)
    date_crime_received = db.Column(db.DateTime, nullable=False, default=func.now())
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #def __repr__(self):
    #    return f'<Crime "{self.crime_id}", "{self.date_of_incident}", "{self.issued_by}",
    #    "{self.time_of_incident}", "{self.incident_location}">'

class Theft(db.Model, UserMixin):
    theft_id = db.Column(db.Integer, primary_key=True)
    place_of_theft = db.Column(db.String(50), nullable=False)
    street_address = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(10), nullable=False)
    date_of_theft = db.Column(db.String(10), nullable=False)
    reported_by = db.Column(db.String(10), nullable=True)
    phone_number = db.Column(db.String(10), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    time_of_theft = db.Column(db.String(10), nullable=False)
    stolen_property = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    theft_status = db.Column(db.String(10), nullable=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    theft_file_upload = db.Column(db.Text, nullable=True)
    theft_file_name = db.Column(db.Text, nullable=True)
    theft_mimetype = db.Column(db.Text, nullable=True)
    date_theft_received = db.Column(db.DateTime, nullable=False, default=func.now())
    victim_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Message(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)
    email_address = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text, nullable=True)
    date_received = db.Column(db.DateTime, nullable=False, default=func.now())
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))