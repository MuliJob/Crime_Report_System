from flask import Flask
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import NEWS_API, SECRET_KEY
from flask_session import Session
from flask_migrate import Migrate
#from flask_admin import Admin

api_key = NEWS_API

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///system.db'
app.config["SESSION_PERMANENT"]=False
app.config['SESSION_TYPE']='filesystem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)
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