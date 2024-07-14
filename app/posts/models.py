from datetime import datetime
from app import db
from flask_login import UserMixin
import pytz

def current_time():
    return datetime.now(pytz.timezone('Africa/Nairobi'))

class Crime(db.Model, UserMixin):
    crime_id = db.Column(db.Integer, primary_key=True)
    date_of_incident = db.Column(db.String(10), nullable=False)
    issued_by = db.Column(db.String(20), nullable=True)
    time_of_incident = db.Column(db.String(10), nullable=False)
    phonenumber = db.Column(db.String(10), nullable=True)
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
    date_crime_received = db.Column(db.DateTime(timezone=True), default=current_time())
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def to_dict(self):
        return {
            'crime_id': self.crime_id,
            'date_of_incident': self.date_of_incident,
            'issued_by': self.issued_by,
            'time_of_incident': self.time_of_incident,
            'phonenumber': self.phonenumber,
            'incident_location': self.incident_location,
            'incident_nature': self.incident_nature,
            'incident_details': self.incident_details,
            'suspect_details': self.suspect_details,
            'arrest_history': self.arrest_history,
            'suspect_name': self.suspect_name,
            'comments': self.comments,
            'crime_status': self.crime_status,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'date_crime_received': self.date_crime_received.isoformat(),
            'reporter_id': self.reporter_id
        }

    #def __repr__(self):
    #    return f'<Crime "{self.crime_id}", "{self.date_of_incident}", "{self.issued_by}",
    #    "{self.time_of_incident}", "{self.incident_location}">'

class Message(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)
    email_address = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text, nullable=True)
    date_received = db.Column(db.DateTime(timezone=True), default=current_time())
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email_address': self.email_address,
            'message': self.message,
            'reply': self.reply,
            'date_received': self.date_received.isoformat(),
            'sender_id': self.sender_id
        }