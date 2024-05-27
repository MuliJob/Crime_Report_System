from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 3}
app.config['SECRET_KEY'] = '\x08\xd9V7\x94\xf0\xce\xa47\n;N\x86\xcak\xbd\x96bP\xed&Z`\x8ep\x0cJ\xf9S\x1b\x1b\xf8\xfd\xd3-c\xc0f\xfe\xb6\x18\xder2\xef\x8f!\xb6N\r\xe6o\x182{\xc5a\xc2=\xd5c\x87n\xd3'
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'crime.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'sign_in'


from app import views
from app import models