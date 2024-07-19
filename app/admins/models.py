
from flask import current_app
from itsdangerous import Serializer
from app import db
from flask_login import UserMixin

class Admin(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(10), nullable=False)
  password = db.Column(db.String(255), nullable=False)
  admin_email = db.Column(db.String(120), unique=True, nullable=False)
  
  def get_admin_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'admin_id': self.id}, salt='admin-password-reset-salt')

  @staticmethod
  def verify_admin_reset_token(token, expires_sec=1800):
      s = Serializer(current_app.config['SECRET_KEY'])
      try:
          admin_id = s.loads(token, salt='admin-password-reset-salt', max_age=expires_sec)['admin_id']
      except:
          return None
      return Admin.query.get(admin_id)

  def __repr__(self):
    return f'Admin("{self.username}", "{self.id}")'
  
#create table

#insert admin data onetime
#admin=Admin(username='admin', password=generate_password_hash('87654321', method='pbkdf2:sha256'))
