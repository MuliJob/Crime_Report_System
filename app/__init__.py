from flask import Flask, current_app, flash
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import SECRET_KEY, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER, SQLALCHEMY_DATABASE_URI
from flask_session import Session
from flask_migrate import Migrate
from flask_mail import Mail, Message

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config["SESSION_PERMANENT"]=False
app.config['SESSION_TYPE']='filesystem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# sending email when report is submitted
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD 
app.config['MAIL_DEFAULT_SENDER'] = MAIL_DEFAULT_SENDER

mail = Mail(app)
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)
Session(app)

login_manager = LoginManager(app)
login_manager.login_view = 'users.sign_in'

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)

# login_manager.login_view = 'officers.officerLogin'

# @login_manager.user_loader
# def load_officer(officer_id):
#    return Officers.query.get(officer_id)

#@login_manager.user_loader
#def load_user(id):
#  return models.User.query.get(int(id))

# sending email to admin
def send_admin_email(subject, body):
    try:
        admin = Admin.query.first()
        if not admin:
            print("Admin email not found")
            return False
        
        msg = Message(subject,
                      recipients=[admin.admin_email])  # Admin's email address
        msg.body = body
        mail.send(msg)
        print("Email send successful")
        return True
    
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False
    
# sending email when officer is assigned
def send_assignment_email(officer, report):
    subject = f"New Case Assignment: Report #{report.report_id}"
    body = f"""
    Dear {officer.first_name},

    You have been assigned to a new case:

    Report ID: {report.report_id}
    Crime Type: {report.crime_type}
    Location: {report.location}
    Date: {report.date}
    Time: {report.time}
    Priority: {report.urgency}
    Deadline: {report.deadline}

    Please log in to the system for more details.

    Best regards,
    Admin Team
    """
    try:
        msg = Message(subject,
                      sender=current_app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[officer.officer_email])
        msg.body = body
        mail.send(msg)
        flash('Email notification sent', 'success')
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        flash('Failed to send email notification', 'warning')

# from app.officers.models import Officers
from app.users.routes import users
from app.posts.routes import posts
from app.main.routes import main
from app.admins.routes import admins
from app.officers.routes import officers
from app.users import models
from app.admins.models import Admin


app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)
app.register_blueprint(admins)
app.register_blueprint(officers)