from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user
from app.posts.models import Crime, Theft
from app import db, send_admin_email
from werkzeug.utils import secure_filename

posts = Blueprint('posts', __name__)

@posts.route('/theft_report', methods=['GET', 'POST'])
def report_theft(): 

    victim = current_user.id

    if request.method == 'POST':
        place_of_theft = request.form.get('place_of_theft')
        street_address = request.form.get('street_address')
        city = request.form.get('city')
        date_of_theft = request.form.get('date_of_theft')
        reported_by = request.form.get('reported_by')
        phone_number = request.form.get('phone_number')
        value = request.form.get('value')
        time_of_theft = request.form.get('time_of_theft')
        stolen_property = request.form.get('stolen_property')
        description = request.form.get('description')
        theft_image = request.files['theft_image']

        filename = secure_filename(theft_image.filename)
        mimetype = theft_image.mimetype

        theft_report = Theft(place_of_theft=place_of_theft, 
                                street_address=street_address,
                                city=city, 
                                date_of_theft=date_of_theft,
                                reported_by=reported_by,
                                phone_number=phone_number, 
                                value=value,
                                time_of_theft=time_of_theft, 
                                stolen_property=stolen_property,
                                description=description,
                                theft_file_upload=theft_image.read(),
                                theft_file_name=filename,
                                theft_mimetype=mimetype,
                                victim_id=victim)
        try:
            db.session.add(theft_report)
            db.session.commit()

            #sending email
            subject = f"New Theft Report Sent: {theft_report.stolen_property}"
            body = f"""
                A new theft report has been sent:

                Place Of Theft: {theft_report.place_of_theft}
                Location: {theft_report.street_address}
                Date: {theft_report.date_of_theft}
                Time: {theft_report.time_of_theft}

                Please review this report as soon as possible.
            """
            if send_admin_email(subject, body):
                flash("Report submitted successfully and admin has been notified.", "success")
            else:
                flash("Report submitted successfully, but there was an issue notifying the admin.", "warning")

            return redirect(url_for('users.user_dashboard'))
        except Exception:
            # Handle database errors gracefully (e.g., log the error)
            flash(f"An error occurred! Please try again", category='danger')
            return render_template('user/report_theft.html')

    return render_template('user/report_theft.html')


@posts.route('/crime_report', methods=['GET', 'POST'])
def report_crime():

    reporter = current_user.id

    if request.method == 'POST':
        date_of_incident = request.form.get('date_of_incident')
        issued_by = request.form.get('issued_by')
        time_of_incident = request.form.get('time_of_incident')
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
                                incident_location=incident_location,
                                incident_nature=incident_nature, 
                                incident_details=incident_details,
                                suspect_details=suspect_details, 
                                arrest_history=arrest_history,
                                suspect_name=suspect_name,
                                comments=comments,
                                crime_file_upload=image.read(),
                                crime_file_name=filename,
                                crime_mimetype=mimetype,
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
            # Handle database errors gracefully (e.g., log the error)
            flash(f"An error occurred! Please try again", category='danger')
            return render_template('user/report_crime.html')
        
    return render_template('user/report_crime.html')