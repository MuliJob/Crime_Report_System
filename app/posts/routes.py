from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, session, url_for, request, flash
from flask_login import current_user, login_required
from app.posts.models import Crime, Message
from app import db, send_admin_email
from werkzeug.utils import secure_filename

posts = Blueprint('posts', __name__)


# submitting crime report
@posts.route('/crime_report', methods=['GET', 'POST'])
def report_crime():

    reporter = current_user.id

    # Get location from session or database
    latitude = session.get('latitude')
    longitude = session.get('longitude')

    if request.method == 'POST':
        date_of_incident = request.form.get('date_of_incident')
        issued_by = request.form.get('issued_by')
        time_of_incident = request.form.get('time_of_incident')
        phonenumber = request.form.get('phonenumber')
        incident_location = request.form.get('incident_location')
        incident_nature = request.form.get('incident_nature')
        incident_details = request.form.get('incident_details')
        suspect_details = request.form.get('suspect_details')
        arrest_history = request.form.get('arrest_history')
        suspect_name = request.form.get('suspect_name')
        comments = request.form.get('comments')
        image = request.files['image']


        filename = secure_filename(image.filename)
        mimetype = image.mimetype

        crime_report = Crime(date_of_incident=date_of_incident, 
                                issued_by=issued_by,
                                time_of_incident=time_of_incident, 
                                phonenumber=phonenumber,
                                incident_location=incident_location,
                                incident_nature=incident_nature, 
                                incident_details=incident_details,
                                suspect_details=suspect_details, 
                                arrest_history=arrest_history,
                                suspect_name=suspect_name,
                                comments=comments,
                                latitude=latitude,
                                longitude=longitude,
                                crime_file_upload=image.read(),
                                crime_file_name=filename,
                                crime_mimetype=mimetype,
                                date_crime_received=datetime.now(timezone.utc),
                                reporter_id=reporter)
        try:
            db.session.add(crime_report)
            db.session.commit()

            #sending email
            subject = f"New Crime Report Sent: {crime_report.incident_nature}"
            body = f"""
                A new theft report has been sent:

                Location: {crime_report.incident_location}
                Date: {crime_report.date_of_incident}
                Time: {crime_report.time_of_incident}

                Please review this report as soon as possible.
            """
            if send_admin_email(subject, body):
                flash("Report submitted successfully and admin has been notified.", "success")
            else:
                flash("Report submitted successfully, but there was an issue notifying the admin.", "warning")

            return redirect(url_for('users.user_dashboard'))
        except Exception:
            flash(f"An error occurred! Please try again", category='danger')
            return render_template('user/report_crime.html')
        
    return render_template('user/report_crime.html')

# contact us
@posts.route('/users/contactus', methods=["POST","GET"])
@login_required
def contact_us():
    sender = current_user.id

    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        message = request.form.get('message')

        sender_message = Message(
            first_name=firstName,
            last_name=lastName,
            email_address=email,
            message=message,
            datetime_received=datetime.now(timezone.utc),
            sender_id=sender
        )
        try:
            db.session.add(sender_message)
            db.session.commit()

            subject = f"New Message Sent"
            body = f"""
                You have a new message from: {sender_message.first_name}
            """
            if send_admin_email(subject, body):
                flash("Message sent successfully wait for feedback from admin.", "success")
            else:
                flash("Message sent successfully, but there was an issue notifying the admin.", "warning")

            return redirect(url_for('posts.contact_us'))
        except Exception:
            flash(f"An error occurred! Please try again", category='danger')
            return render_template('user/contactus.html')
        
    return render_template('/user/contactus.html')