from datetime import datetime, timedelta
from io import BytesIO
from flask import Blueprint, abort, current_app, render_template, redirect, request, flash, send_file, session, url_for
from flask_login import logout_user
import folium
from sqlalchemy import extract, func
from app.admins.models import Admin 
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.officers.models import CaseReport, Officers
from app.posts.models import Crime, Message
from app.users.models import User
from functools import wraps
from folium.plugins import HeatMap


admins = Blueprint('admins', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            flash('You need to be logged in as an admin to access the page.', 'danger')
            return redirect(url_for('admins.adminIndex'))
        return f(*args, **kwargs)
    return decorated_function

# getting coordinates
def get_coordinates():
    return db.session.query(Crime.latitude, Crime.longitude).all()

# function to get crime by month
def get_crime_data_by_month():
    crime_data = {f'{i:02d}': 0 for i in range(1, 13)}
    results = db.session.query(
        db.extract('month', Crime.date_crime_received).label('month'),
        db.func.count(Crime.crime_id).label('count')
    ).group_by('month').all()

    for month, count in results:
        crime_data[f'{month:02d}'] = count

    return crime_data

# getting daily distribution
def get_daily_crime_data():
    now = datetime.now()

    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    end_of_week = start_of_week + timedelta(days=6)
    end_of_week = end_of_week.replace(hour=23, minute=59, second=59, microsecond=999999)

    crime_dist = {day: {'crimes': 0} for day in range(7)}  

    crime_results = db.session.query(
        extract('dow', Crime.date_crime_received).label('day'),
        func.count(Crime.crime_id).label('count')
    ).filter(
        Crime.date_crime_received >= start_of_week,
        Crime.date_crime_received <= end_of_week
    ).group_by('day').all()

    

    for day, count in crime_results:
        crime_dist[day]['crimes'] = count

    return crime_dist

# getting monthly averages
def get_monthly_averages():
    crime_average = {f'{i:02d}': 0 for i in range(1, 13)}

    crime_results = db.session.query(
        extract('month', Crime.date_crime_received).label('month'),
        func.count(Crime.crime_id).label('count')
    ).group_by('month').all()

    for month, count in crime_results:
        crime_average[f'{month:02d}'] = count

    

    return crime_average

#getting annual crime distribution
def get_annual_crime_data():
    annual_crime_data = db.session.query(
        func.strftime('%Y', Crime.date_crime_received).label('year'),
        func.count(Crime.crime_id).label('crime_count')
    ).group_by(func.strftime('%Y', Crime.date_crime_received)).all()

    return annual_crime_data

# admin login page route
@admins.route('/admin/', methods=['GET', 'POST'])
def adminIndex():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == '' and password == '':
            flash('Please fill all the field', category='danger')
            return redirect('/admin/')
        else:
            admins = Admin().query.filter_by(username=username).first()
            if admins and check_password_hash(admins.password,password):
                session['admin_id']=admins.id
                session['admin_name']=admins.username
                flash('Login Successfully', category='success')
                return redirect('/admin/dashboard')
            else:
                flash("Invalid Email and Password", category='danger')
                return redirect('/admin/')
    else:   
        return render_template('admin/index.html', 
        title='Admin Login')

@admins.route('/admin/dashboard')
@admin_required
def adminDashboard():
    annual_crime_data = get_annual_crime_data()
    crime_average = get_monthly_averages()
    crime_data = get_crime_data_by_month()
    crime_dist = get_daily_crime_data()
    user_count = User.query.count()
    crime_count = Crime.query.count()
    
    recovered_count = Crime.query.filter_by(crime_status='Recovered').count()
    crimes = Crime.query.all()
    crime_locations = [crime.to_dict() for crime in crimes]

    return render_template('admin/dashboard.html', user_count=user_count,
                           crime_count=crime_count, 
                           recovered_count=recovered_count, 
                           crime_data=crime_data,
                           crime_average=crime_average,
                           annual_crime_data=annual_crime_data,
                           crime_locations=crime_locations,
                           crime_dist=crime_dist)

# change admin password
@admins.route('/admin/change-admin-password',methods=["POST","GET"])
@admin_required
def adminChangePassword():
    admin=Admin.query.get(1)
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if username == "" or password=="":
            flash('Please fill the field','danger')
            return redirect('/admin/change-admin-password')
        else:
            Admin().query.filter_by(username=username).update(dict(password=generate_password_hash(
                                password, 
                                method='pbkdf2:sha256')))
            db.session.commit()
            flash('Admin Password update successfully','success')
            return redirect('/admin/change-admin-password')
    else:
        return render_template('admin/admin-change-password.html',title='Admin Change Password',admin=admin)


@admins.route('/admin/reports')
@admin_required
def reports():
    search_query = request.args.get('search_query', '')
    try:
        if search_query:
            crimes = Crime.query.filter(
                Crime.incident_location.ilike(f'%{search_query}%') | 
                Crime.issued_by.ilike(f'%{search_query}%') |
                Crime.date_of_incident.ilike(f'%{search_query}%') |
                Crime.time_of_incident.ilike(f'%{search_query}%') |
                Crime.date_crime_received.ilike(f'%{search_query}%') |
                Crime.crime_status.ilike(f'%{search_query}%') |
                Crime.incident_nature.ilike(f'%{search_query}%')
            ).all()
        else:
            crimes = Crime.query.all()
    except:
        current_app.logger.error("Database error:")
        
        flash("No reports with the keyword.", "warning")
        
        return redirect(url_for('admins.reports'))
    
    return render_template('admin/reports.html', title='Reports Dashboard', crimes=crimes)




@admins.route('/admin/crime_status/<int:crime_id>', methods=['POST'])
@admin_required
def updateCrimeStatus(crime_id):
    try:
        crime = Crime.query.get_or_404(crime_id)
        crime_status = request.form.get('crime_status')
        if crime_status:
            crime.crime_status = crime_status
            db.session.commit()
            flash(f'Crime status updated to {crime_status}.', 'success')
        else:
            flash('Failed to update crime status.', 'danger')
    except:
        current_app.logger.error("Database error:")
        
        flash("An error occurred. Please try again later.", "danger")
        
        return redirect(url_for('admins.crimeStatus'))
    return redirect(url_for('admins.crimeStatus'))

@admins.route('/admin/crime_status')
@admin_required
def crimeStatus():
    search_crime = request.args.get('search_crime', '')
    try:
        if search_crime:
            crimes_status = Crime.query.filter(
                Crime.incident_location.ilike(f'%{search_crime}%') | 
                Crime.issued_by.ilike(f'%{search_crime}%') |
                Crime.date_of_incident.ilike(f'%{search_crime}%') |
                Crime.time_of_incident.ilike(f'%{search_crime}%') |
                Crime.date_crime_received.ilike(f'%{search_crime}%') |
                Crime.crime_status.ilike(f'%{search_crime}%')
            ).all()
        else:
            crimes_status = Crime.query.all()
    except:
        current_app.logger.error("Database error:")
        
        flash("No report with the keyword.", "warning")
        
        return redirect(url_for('admins.crimeStatus'))

    return render_template('admin/crime_status.html', title='Crime Status', crimes_status=crimes_status)

@admins.route('/admin/crime_details/<int:crime_id>', methods=['POST', 'GET'])
@admin_required
def crimeDetails(crime_id):
    try:
        crime_details = Crime.query.filter_by(crime_id=crime_id).all()
        if crime_details is None:
            flash("Crime details not found.", "warning")
            return redirect(url_for('admins.reports'))
    except:
        # Log the error
        current_app.logger.error("Database error:")
        
        # Flash an error message to the user
        flash("An error occurred while fetching the reports crime details. Please try again later.", "danger")
        
        # Redirect to a safe page, like the admin dashboard
        return redirect(url_for('admins.reports'))
    
    return render_template('admin/crime_details.html', crime_details=crime_details)

@admins.route('/admin/crimes_details/<int:crime_id>', methods=['POST', 'GET'])
@admin_required
def caseReport(crime_id):
    if request.method == 'POST':
        crime_type = request.form.get('crime_type')
        location = request.form.get('location')
        date = request.form.get('date')
        time = request.form.get('time')
        description = request.form.get('description')
        evidence = request.form.get('evidence')
        urgency = request.form.get('urgency')

        case_report = CaseReport(crime_type=crime_type,
                                 location=location,
                                 date=date,
                                 time=time,
                                 description=description,
                                 evidence=evidence,
                                 urgency=urgency)
        try:
            db.session.add(case_report)
            db.session.commit()
            flash('Success. Case Report created', 'success')
        except Exception as e:
            current_app.logger.error(f"Database error: {str(e)}")
            flash("An error occurred when creating report. Please try again later.", "danger")
        
        # Redirect to the same page (crime details) after processing
        return redirect(url_for('admins.crimeDetails', crime_id=crime_id))

    # If it's a GET request, just render the page
    return redirect(url_for('admins.crimeDetails', crime_id=crime_id))


@admins.route('/admin/case-reports')
@admin_required
def case_reports():
    cases = CaseReport.query.all()
    officers = Officers.query.all()
    return render_template('admin/case_reports.html', cases=cases, officers=officers)

# @admins.route('/admins/assign_officer/<int:report_id>', methods=['POST'])
# def assign_officer(report_id):
#     officer_id = request.form.get('officer_id')

#     # Update case report with assigned officer
#     case_report = CaseReport.query.get_or_404(report_id)
#     case_report.assigned_officer_id = officer_id

#     db.session.commit()

#     return redirect(url_for('admins.case_reports', case_report=case_report))


@admins.route('/admin/case_report_details/<int:report_id>')
@admin_required
def case_report_details(report_id):
    report = CaseReport.query.get_or_404(report_id)
    return render_template('admin/case_report_details.html', report=report)

@admins.route('/admin/edit_case_report/<int:report_id>', methods=['GET', 'POST'])
@admin_required
def edit_case_report(report_id):
    report = CaseReport.query.get_or_404(report_id)
    officers = Officers.query.all()
    
    if request.method == 'POST':
        # Update the report with form data
        report.crime_type = request.form['crime_type']
        report.location = request.form['location']
        report.date = request.form['date']
        report.time = request.form['time']
        report.description = request.form['description']
        report.evidence = request.form['evidence']
        report.urgency = request.form['urgency']
        
        try:
            db.session.commit()
            flash('Report updated successfully', 'success')
            return redirect(url_for('admins.case_reports'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    # For GET request, render the form with existing data
    return render_template('admin/edit_case_report.html', report=report, officers=officers)
    
# download route for download files
@admins.route('/admin/crime_details/<int:crime_id>')
@admin_required
def download(crime_id):
    try:
        upload = Crime.query.filter_by(crime_id=crime_id).first()
        if not upload:
            abort(404, description="Crime record not found")
        
        if not upload.crime_file_upload or not upload.crime_file_name:
            abort(404, description="File not found")
        
        return send_file(
            BytesIO(upload.crime_file_upload),
            download_name=upload.crime_file_name,
            as_attachment=True,
            mimetype=upload.crime_mimetype
        )
    except Exception as e:
        # Log the error
        print(f"Error downloading file: {str(e)}")
        abort(500, description="Internal server error")
    

@admins.route('/admin/analytics')
@admin_required
def analytics():
    # Get coordinates from database
    coordinates = get_coordinates()
    
    map_center = [sum(lat for lat, _ in coordinates) / len(coordinates),
                  sum(lon for _, lon in coordinates) / len(coordinates)]
    m = folium.Map(location=map_center, zoom_start=6)
    
    HeatMap(coordinates).add_to(m)
    
    map_html = m._repr_html_()
    try:
        crime_data = db.session.query(
            Crime.incident_location, db.func.count(Crime.crime_id)
        ).group_by(Crime.incident_location).all()

        crime_labels = [row[0] for row in crime_data]
        crime_counts = [row[1] for row in crime_data]
        
    except:
        current_app.logger.error("Database error:")
        
        flash("An error occurred generating the analysis.", "danger")
        
        return redirect(url_for('admins.analytics'))

    return render_template('admin/analytics.html', title='Analytics Dashboard', 
                            crime_labels=crime_labels, crime_counts=crime_counts,
                            map_html=map_html)

@admins.route('/admin/notifications')
@admin_required
def notifications():
    search_notifications = request.args.get('search_notifications', '')
    try:
        if search_notifications:
            messages = Message.query.filter(
                Message.incident_location.ilike(f'%{search_notifications}%') | 
                Message.issued_by.ilike(f'%{search_notifications}%') |
                Message.date_of_incident.ilike(f'%{search_notifications}%') |
                Message.time_of_incident.ilike(f'%{search_notifications}%') |
                Message.date_received.ilike(f'%{search_notifications}%') |
                Message.crime_status.ilike(f'%{search_notifications}%')
            ).all()
        else:
            messages = Message.query.all()
    except:
        # Log the error
        current_app.logger.error("Database error:")
        
        # Flash an error message to the user
        flash("No report with the keyword.", "warning")
        
        # Redirect to a safe page, like the admin dashboard
        return redirect(url_for('admins.notifications'))
    return render_template('/admin/notifications.html', messages=messages)

@admins.route('/admin/message/<int:id>', methods=['GET', 'POST'])
@admin_required
def view_message(id):
    try:
        message = Message.query.get(id)
        if message is None:
            flash("Message not found.", "warning")
            return redirect(url_for('admins.notifications'))

        if request.method == 'POST':
            message_reply = request.form.get('reply')
            if message_reply:
                message.reply = message_reply
                db.session.commit()
                flash('Reply sent.', 'success')
            else:
                flash('Failed to send reply.', 'danger')
                
            return redirect(url_for('admins.view_message', id=id))

    except Exception as e:
        # Log the error with details
        current_app.logger.error(f"Database error: {e}")
        
        # Flash an error message to the user
        flash("An error occurred. Please try again later.", "danger")
        
        # Redirect to a safe page
        return redirect(url_for('admins.notifications'))
    
    return render_template('/admin/message_details.html', message=message)

@admins.route('/admin/logout')
@admin_required
def adminLogout():    
    if not session.get('admin_id'):
        return redirect('/admin/')
    if session.get('admin_id'):
        session['admin_id']=None
        session['admin_name']=None
        flash('You have been logged out.', category='info')
        logout_user()
    return redirect(url_for('admins.adminIndex'))
