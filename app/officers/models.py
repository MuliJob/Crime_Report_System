from datetime import datetime
from app import db
from flask_login import UserMixin
  
class Officers(db.Model, UserMixin):
    officer_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    officer_email = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)
    badge = db.Column(db.String(20), nullable=False)
    rank = db.Column(db.String(10), nullable=False)
    station = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    assignments = db.relationship('CaseReport', backref='assigned_officer', lazy=True)
    def to_dict(self):
      return {
          'officer_id': self.officer_id,
          'username': self.username,
          'officer_email': self.officer_email,
          'first_name': self.first_name,
          'last_name': self.last_name,
          'badge': self.badge,
          'rank': self.rank,
          'station': self.station,
          'password': self.password,
      }
    

class CaseReport(db.Model, UserMixin):
    report_id = db.Column(db.Integer, primary_key=True)
    crime_type = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(40), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=False)
    evidence = db.Column(db.Text, nullable=False)
    urgency = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    assigned_officer_id = db.Column(db.Integer, db.ForeignKey('officers.officer_id'))

    def __repr__(self):
        return f'<CaseReport {self.report_id}>'

    def to_dict(self):
       return {
          'reporter_id': self.reporter_id,
          'crime_type': self.crime_type,
          'location': self.location,
          'date': self.date,
          'time': self.time,
          'description': self.description,
          "evidence": self.evidence,
          'urgency': self.urgency,
       }

