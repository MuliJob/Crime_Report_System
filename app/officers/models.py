from app import db
from flask_login import UserMixin

class Officer(db.Model, UserMixin):
  officer_id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(100), nullable=False)
  last_name = db.Column(db.String(100), nullable=True)
  officer_email = db.Column(db.String(120), nullable=False)
  badge = db.Column(db.String(20), nullable=False)
  rank = db.Column(db.String(10), nullable=False)
  station = db.Column(db.String(20), nullable=False)


  def to_dict(self):
      return {
          'officer_id': self.officer_id,
          'first_name': self.first_name,
          'last_name': self.last_name,
          'officer_email': self.officer_email,
          'badge': self.badge,
          'rank': self.rank,
          'station': self.station,
      }