from functools import wraps
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, logout_user
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

from app.officers.models import CaseReport, Officers

officers = Blueprint('officers', __name__)

def officer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('officer_id'):
            flash('You need to be logged in as an officer to access the page.', 'danger')
            return redirect(url_for('officers.officerLogin'))
        return f(*args, **kwargs)
    return decorated_function

@officers.route('/officer/login', methods=['GET', 'POST'])
def officerLogin():
  if  session.get('officer_id'):
        return redirect('/officer/officer-dashboard')
  if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        officer = Officers.query.filter_by(username=username).first()
        
        if officer:
            if check_password_hash(officer.password, password):
                session['officer_id']=officer.officer_id
                session['officer_username']=officer.username
                flash(f'Logged in successfully! Hello {username}', category='success')
                return redirect(url_for('officers.officerDashboard'))
            else: 
                flash('Incorrect password, try again.', category='danger')
        else:
            flash('Username does not exist.', category='danger')
    
  return render_template('officer/login.html')

@officers.route('/officer/register', methods=['GET', 'POST'])
def officerRegister():
  if  session.get('officer_id'):
        return redirect('/officer/officer-dashboard')
  if request.method == 'POST':
        username = request.form.get('username')
        officer_email = request.form.get('officer_email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        badge = request.form.get('badge')
        rank = request.form.get('rank')
        station = request.form.get('station')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        officer = Officers.query.filter_by(username=username).first()
        email = Officers.query.filter_by(officer_email=officer_email).first()

        if officer:
          flash('Username already exists.', category='danger')
        elif email:
          flash('Email already exists.', category='danger')
        elif len(username) < 2:
            flash('Username must be more than 1 characters.', category='danger')
        elif len(officer_email) < 4:
            flash('Email must be more than 4 characters.', category='danger')
        elif password1 != password2:
            flash('Password don\'t match.', category='danger')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='danger')
        else:
            # add officer to database
            new_officer = Officers(username=username, 
                                officer_email=officer_email, 
                                first_name=first_name,
                                last_name=last_name,
                                badge=badge,
                                rank=rank,
                                station=station,
                                password=generate_password_hash(
                                password1, 
                                method='pbkdf2:sha256'))
            db.session.add(new_officer)
            db.session.commit()
            flash('Account created! Login to Access the Dashboard', category='success')
            return redirect(url_for('officers.officerLogin'))
  return render_template('officer/registration.html')

@officers.route('/officer/officer-dashboard', methods=['GET', 'POST'])
@officer_required
def officerDashboard():
    # Check if the user is logged in
    if 'officer_id' not in session:
        return redirect(url_for('login'))

    officer_id = session['officer_id']
    
    # Get the officer
    officer = Officers.query.get(officer_id)
    if not officer:
        return redirect(url_for('officers.officerLogin'))

    # Get all cases assigned to the current officer
    all_cases = CaseReport.query.filter_by(assigned_officer_id=officer_id).all()
    all_cases_count = len(all_cases)

    # Get completed cases
    completed_cases = CaseReport.query.filter_by(assigned_officer_id=officer_id, status='completed').all()
    completed_cases_count = len(completed_cases)

    return render_template('officer/officer-dashboard.html', 
                           all_cases_count=all_cases_count, 
                           completed_cases_count=completed_cases_count)

@officers.route('/officer/assigned-cases')
@officer_required
def assignedCase():
    officer_id = session['officer_id']
        
    all_cases_assigned = CaseReport.query.filter_by(assigned_officer_id=officer_id).all()

    return render_template('officer/assigned-cases.html', all_cases_assigned=all_cases_assigned)

@officers.route('/officer/case-details/<int:report_id>', methods=['POST','GET'])
@officer_required
def caseDetails(report_id):
    try:
        report = CaseReport.query.get_or_404(report_id)

        if report is None:
                flash("Case details not found.", "warning")
                return redirect(url_for('admins.reports'))
        
        if request.method == 'POST':
            officer_report_text = request.form.get('officer_report')
            
            report.reports = officer_report_text
            
            try:
                db.session.commit()
                flash('Report saved successfully', 'success')
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error saving officer report: {str(e)}")
                flash(f'An error occurred while saving the report. Please try again.', 'danger')

        return render_template('/officer/officer-case-details.html', report=report)
    except:
        current_app.logger.error("Database error:")
        flash("An error occurred while fetching the case report details. Please try again later.", "danger")
        return redirect(url_for('officers.assignedCase'))

@officers.route('/officer/settled-cases')
@officer_required
def settledCase():
    return render_template('/officer/settled-cases.html', )

@officers.route('/officer/logout')
@officer_required
def officerLogout():    
    if not session.get('officer_id'):
        return redirect('/officer/login')
    if session.get('officer_id'):
        session['officer_id']=None
        session['officer_username']=None
        flash('You have been logged out.', category='info')
        logout_user()
    return redirect(url_for('officers.officerLogin'))