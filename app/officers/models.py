from flask import current_app
from itsdangerous import Serializer
import pytz
from datetime import datetime
from app import db
from flask_login import UserMixin
  
def current_time():
    return datetime.now(pytz.timezone('Africa/Nairobi'))
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
    assignments = db.relationship('CaseReport', back_populates='assigned_officer', lazy=True)
    
    def get_officer_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'officer_id': self.officer_id}, salt='officer-password-reset-salt')

    @staticmethod
    def verify_officer_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            officer_id = s.loads(token, salt='officer-password-reset-salt', max_age=expires_sec)['officer_id']
        except:
            return None
        return Officers.query.get(officer_id)

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
        }

    def get_id(self):
        return str(self.officer_id)
    

class CaseReport(db.Model, UserMixin):
    report_id = db.Column(db.Integer, primary_key=True)
    crime_type = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(40), nullable=False)
    phone_number = db.Column(db.String(10))
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=False)
    evidence = db.Column(db.Text, nullable=False)
    urgency = db.Column(db.String(10), nullable=False)
    deadline = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    reports = db.Column(db.Text, nullable=True)
    media = db.Column(db.Text, nullable=True)
    filename = db.Column(db.Text, nullable=True)
    mimetype = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=current_time())
    assigned_officer_id = db.Column(db.Integer, db.ForeignKey('officers.officer_id'))
    assigned_officer = db.relationship('Officers', back_populates='assignments')

    def __repr__(self):
        return f'<CaseReport {self.report_id}>'

    def to_dict(self):
        return {
            'report_id': self.report_id,  
            'crime_type': self.crime_type,
            'location': self.location,
            'date': self.date,
            'time': self.time,
            'description': self.description,
            "evidence": self.evidence,
            'urgency': self.urgency,
            'deadline': self.deadline,
            'assigned_officer_id': self.assigned_officer_id,  
            'status': self.status, 
            'created_at': self.created_at.isoformat() if self.created_at else None,  
        }
    # @classmethod
    # def get_recent_cases_count(cls, officer_id, hours=12):
    #     try:
    #         return db.session.query(cls).filter_by(
    #             assigned_officer_id=officer_id
    #         ).filter(cls.created_at >= func.date_sub(func.now(), interval=f'{hours} day')).count()
    #     except Exception as e:
    #         current_app.logger.error(f"Error querying recent cases: {str(e)}")
    #         return 0

