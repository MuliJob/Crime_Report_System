
from app import db
from flask_login import UserMixin

class Admin(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(10), nullable=False)
  password = db.Column(db.String(255), nullable=False)
  admin_email = db.Column(db.String(120), unique=True, nullable=False)

  def __repr__(self):
    return f'Admin("{self.username}", "{self.id}")'
  
#create table

#insert admin data onetime
#admin=Admin(username='admin', password=generate_password_hash('87654321', method='pbkdf2:sha256'))
