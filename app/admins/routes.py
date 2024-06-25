from flask import Blueprint, current_app, render_template, redirect, request, flash, session, url_for
from flask_login import logout_user
from app.admins.models import Admin 
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.posts.models import Crime, Theft
from app.users.models import User
from functools import wraps

admins = Blueprint('admins', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            flash('You need to be logged in as an admin to access the page.', 'danger')
            return redirect(url_for('admins.adminIndex'))
        return f(*args, **kwargs)
    return decorated_function

# admin login
@admins.route('/admin/', methods=['GET', 'POST'])
def adminIndex():
    if request.method == 'POST':
        # get the value of field
        username = request.form.get('username')
        password = request.form.get('password')
        # check the value is not empty
        if username == '' and password == '':
            flash('Please fill all the field', category='danger')
            return redirect('/admin/')
        else:
            # login admin by username
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
    user_count = User.query.count()
    crime_count = Crime.query.count()
    theft_count = Theft.query.count()
    recovered_count = Theft.query.filter_by(status='Recovered').count()
    
    # Fetch trend data for the graph (e.g., monthly counts)
    crime_trends = [30, 50, 70, 60, 90, 100, 200]  # Example data
    theft_trends = [20, 40, 60, 50, 80, 90, 110]   # Example data

    return render_template('admin/dashboard.html', user_count=user_count, crime_count=crime_count, recovered_count=recovered_count, theft_count=theft_count, crime_trends=crime_trends, theft_trends=theft_trends)

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
    try:
        crimes = Crime.query.all()
        thefts = Theft.query.all()
    except:
        # Log the error
        current_app.logger.error("Database error occurred:")
        
        # Flash an error message to the user
        flash("An error occurred while fetching the reports. Please try again later.", "error")
        
        # Redirect to a safe page, like the admin dashboard
        return redirect(url_for('admins.reports'))
    
    return render_template('admin/reports.html', title='Reports Dashboard', crimes=crimes, thefts=thefts)

@admins.route('/admin/reports_status')
@admin_required
def reportStatus():
    try:
        thefts = Theft.query.all()
    except:
        # Log the error
        current_app.logger.error("Database error occurred:")
        
        # Flash an error message to the user
        flash("An error occurred. Please try again later.", "error")
        
        # Redirect to a safe page, like the admin dashboard
        return redirect(url_for('admins.reportStatus'))
    
    return render_template('admin/reports_status.html', title='Reports Status', thefts=thefts)

@admins.route('/admin/reports_status/<int:theft_id>', methods=['POST'])
@admin_required
def updateStatus(theft_id):
    try:
        theft = Theft.query.get_or_404(theft_id)
        status = request.form.get('status')
        if status:
            theft.status = status
            db.session.commit()
            flash(f'Status updated to {status}.', 'success')
        else:
            flash('Failed to update status.', 'danger')
    except:
        # Log the error
        current_app.logger.error("Database error occurred:")
        
        # Flash an error message to the user
        flash("An error occurred. Please try again later.", "error")
        
        # Redirect to a safe page, like the admin dashboard
        return redirect(url_for('admins.updateStatus'))
    
    return redirect(url_for('admins.reportStatus'))

@admins.route('/admin/crime_details/<int:crime_id>')
@admin_required
def crimeDetails(crime_id):
    try:
        # Finding crime by id
        crime_details = Crime.query.filter_by(crime_id=crime_id).all()
    except:
        # Log the error
        current_app.logger.error("Database error occurred:")
        
        # Flash an error message to the user
        flash("An error occurred while fetching the reports crime details. Please try again later.", "error")
        
        # Redirect to a safe page, like the admin dashboard
        return redirect(url_for('admins.reports'))
    
    return render_template('admin/crime_details.html', crime_details=crime_details)

@admins.route('/admin/theft_details/<int:theft_id>')
@admin_required
def theftDetails(theft_id):
    try:
        #Finding theft by id 
        theft_details = Theft.query.filter_by(theft_id=theft_id).all()
    except:
        # Log the error
        current_app.logger.error("Database error occurred:")
        
        # Flash an error message to the user
        flash("An error occurred while fetching the reports theft details. Please try again later.", "error")
        
        # Redirect to a safe page
        return redirect(url_for('admins.reports'))

    return render_template('admin/theft_details.html', theft_details=theft_details)

@admins.route('/admin/analytics')
@admin_required
def analytics():
    try:
        # Fetch crime data grouped by location
        crime_data = db.session.query(
            Crime.incident_location, db.func.count(Crime.crime_id)
        ).group_by(Crime.incident_location).all()

        # Fetch theft data grouped by location
        theft_data = db.session.query(
            Theft.street_address, db.func.count(Theft.theft_id)
        ).group_by(Theft.street_address).all()

        # Prepare data for the charts
        crime_labels = [row[0] for row in crime_data]
        crime_counts = [row[1] for row in crime_data]
        
        theft_labels = [row[0] for row in theft_data]
        theft_counts = [row[1] for row in theft_data]
    except:
        # Log the error
        current_app.logger.error("Database error occurred:")
        
        # Flash an error message to the user
        flash("An error occurred. Please try again later.", "error")
        
        # Redirect to a safe page
        return redirect(url_for('admins.analytics'))

    return render_template('admin/analytics.html', title='Analytics Dashboard', 
                           crime_labels=crime_labels, crime_counts=crime_counts,
                           theft_labels=theft_labels, theft_counts=theft_counts)

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
