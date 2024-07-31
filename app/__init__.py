from flask import Flask, current_app, flash, logging, url_for
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

def send_status_admin_email(subject, body):
    try:
        admin = Admin.query.first()
        if not admin:
            print("Admin email not found")
            return False
        
        msg = Message(subject,
                      recipients=[admin.admin_email])  
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
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        flash('Failed to send email notification', 'warning')

# sending email when status is updated
def send_status_update_email(crime):
    try:
        user = models.User.query.get(crime.reporter_id)  # Assuming there's a user_id field in Crime model
        if user and user.email:
            subject = f"Update on Your Crime Report #{crime.crime_id}"
            body = f"""
            Dear {user.username},

            The status of your crime report (Crime: {crime.incident_nature}) has been updated.

            New Status: {crime.crime_status}

            If you have any questions, please don't hesitate to contact us.

            Best regards,
            Crime Reporting System
            """
            
            msg = Message(subject,
                          sender=current_app.config['MAIL_DEFAULT_SENDER'],
                          recipients=[user.email])
            msg.body = body
            mail.send(msg)
            current_app.logger.info(f"Status update email sent to {user.email} for crime ID {crime.crime_id}")
        else:
            current_app.logger.warning(f"Could not send email for crime ID {crime.crime_id}. User not found or no email address.")
    except Exception as e:
        current_app.logger.error(f"Failed to send status update email: {str(e)}")
        
#sending greeting email
def send_confirmation_email(user):
    subject = "Welcome to Our App!"
    recipients = [user.email]
    body = f"""
    Hello {user.username},

    Thank you for registering with our app. We're excited to have you on board!

    Best regards,
    The E-Security Team
    """

    msg = Message(subject=subject, 
                  sender=current_app.config['MAIL_DEFAULT_SENDER'], 
                  recipients=recipients, 
                  body=body)
    
    try:
        mail.send(msg)
        print(f"Confirmation email sent successfully to {user.email}")
    except Exception as e:
        print(f"Failed to send confirmation email to {user.email}. Error: {str(e)}")
        
#sending user reset email
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('users.reset_token', token=token, _external=True)}

    If you did not make this request then simply ignore this email and no changes will be made.
    Link expires after 30 minutes.
    '''
    mail.send(msg)
    
#sending admin reset email
def send_admin_reset_email(admin):
    token = admin.get_admin_reset_token()
    msg = Message('Password Reset Request',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[admin.admin_email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('admins.resetToken', token=token, _external=True)}

    If you did not make this request then simply ignore this email and no changes will be made.
    Link expires after 30 minutes.
    '''
    mail.send(msg)
    
#sending officer reset email
def send_officer_reset_email(officer):
    token = officer.get_officer_reset_token()
    msg = Message('Password Reset Request',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[officer.officer_email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('officers.resetToken', token=token, _external=True)}

    If you did not make this request then simply ignore this email and no changes will be made.
    Link expires after 30 minutes.
    '''
    mail.send(msg)

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