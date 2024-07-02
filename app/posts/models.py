from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func


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
    date_crime_received = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
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
    date_theft_received = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    victim_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def to_dict(self):
        return {
            'theft_id': self.theft_id,
            'place_of_theft': self.place_of_theft,
            'street_address': self.street_address,
            'city': self.city,
            'date_of_theft': self.date_of_theft,
            'reported_by': self.reported_by,
            'phone_number': self.phone_number,
            'value': self.value,
            'time_of_theft': self.time_of_theft,
            'stolen_property': self.stolen_property,
            'description': self.description,
            'theft_status': self.theft_status,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'date_theft_received': self.date_theft_received.isoformat(),
            'victim_id': self.victim_id
        }

class Message(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)
    email_address = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text, nullable=True)
    date_received = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
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