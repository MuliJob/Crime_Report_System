from flask import current_app
from app import db
from flask_login import UserMixin
from itsdangerous import Serializer


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    crimes = db.relationship('Crime', backref='reporter', lazy=True)
    users = db.relationship('Register', backref='user', uselist=False)
    messages = db.relationship('Message', backref='sender', lazy=True)
    

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='password-reset-salt', max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)
    


class Register(db.Model, UserMixin):
    idno = db.Column(db.Integer, primary_key=True, nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    phonenumber = db.Column(db.String(20), nullable=False)
    residence = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('user.id'))