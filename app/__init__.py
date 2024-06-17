from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import NEWS_API, SECRET_KEY
from flask_session import Session
#from flask_admin import Admin

api_key = NEWS_API

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///system.db'
app.config["SESSION_PERMANENT"]=False
app.config['SESSION_TYPE']='filesystem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Session(app)

login_manager = LoginManager(app)
login_manager.login_view = 'users.sign_in'

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)
#@login_manager.user_loader
#def load_user(id):
#  return models.User.query.get(int(id))

from app.users.routes import users
from app.posts.routes import posts
from app.main.routes import main
from app.admins.routes import admins
from app.users import models

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)
app.register_blueprint(admins)