from app import db


class User(db.Model):
    user_id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    fullname = db.Column(db.String(length=50), nullable=False, unique=False)
    id_no = db.Column(db.Integer(), nullable=False, unique=True)
    phone_number = db.Column(db.String(length=10), nullable=False, unique=True)
    location = db.Column(db.String(length=30), nullable=False)
    gender = db.Column(db.String(length=10), nullable=False)
    