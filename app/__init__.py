from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

db = SQLAlchemy()
DB_NAME = 'system.db'

api_key = '7314a35e75a945b1adfa686c3f81c3a6'

def create_app():
  app = Flask(__name__)
  app.config['SECRET_KEY'] = '\x08\xd9V7\x94\xf0\xce\xa47\n;N\x86\xcak\xbd\x96bP\xed&Z`\x8ep\x0cJ\xf9S\x1b\x1b\xf8\xfd\xd3-c\xc0f\xfe\xb6\x18\xder2\xef\x8f!\xb6N\r\xe6o\x182{\xc5a\xc2=\xd5c\x87n\xd3'
  app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
  db.init_app(app)
  
  from .views import views
  from .auth import auth

  app.register_blueprint(views, url_prefix='/')
  app.register_blueprint(auth, url_prefix='/auth/')

  from .models import Register

  with app.app_context():
    db.create_all()

  login_manager = LoginManager(app)
  login_manager.login_view = 'views.home_page'
  login_manager.init_app(app)

  @login_manager.user_loader
  def load_user(id):
    return Register.query.get(int(id))
  
  return app

def create_database(app):
    if not path.exists('instance/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')