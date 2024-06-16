
from app import db
from werkzeug.security import generate_password_hash
from flask_login import UserMixin

class Admin(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(255), nullable=False)
  password = db.Column(db.String(255), nullable=False)

  def __repr__(self):
    return f'Admin("{self.username}", "{self.id}")'
  
#create table

#insert admin data onetime
#admin=Admin(username='admin', password=generate_password_hash('87654321', method='pbkdf2:sha256'))
