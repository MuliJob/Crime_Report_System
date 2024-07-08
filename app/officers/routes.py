from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, logout_user
from sqlalchemy import func, or_
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
    if 'officer_id' not in session:
        return redirect(url_for('login'))

    officer_id = session['officer_id']
    
    officer = Officers.query.get(officer_id)
    if not officer:
        return redirect(url_for('officers.officerLogin'))

    all_cases = CaseReport.query.filter_by(assigned_officer_id=officer_id).all()
    all_cases_count = len(all_cases)

    completed_cases = CaseReport.query.filter_by(assigned_officer_id=officer_id, status='Solved').all()
    completed_cases_count = len(completed_cases)

    high_urgency_count = CaseReport.query.filter_by(
    assigned_officer_id=officer_id, 
    urgency='high'
    ).count()

    critical_urgency_count = CaseReport.query.filter_by(
        assigned_officer_id=officer_id, 
        urgency='critical'
    ).count()

    urgent_cases_count = high_urgency_count + critical_urgency_count

    recent_cases_count = CaseReport.query.filter_by(
        assigned_officer_id=officer_id
    ).filter(CaseReport.created_at >= (datetime.utcnow() - timedelta(days=3))).count()
    
    recent_activities = db.session.query(
        CaseReport.report_id,
        CaseReport.crime_type,
        CaseReport.created_at
    ).filter_by(
        assigned_officer_id=officer_id
    ).order_by(CaseReport.created_at.desc()).limit(5).all()

    upcoming_deadlines = CaseReport.query.filter_by(
        assigned_officer_id=officer_id
    ).filter(
        CaseReport.deadline >= datetime.utcnow()
    ).order_by(CaseReport.deadline).limit(5).all()

    case_stats = db.session.query(
        CaseReport.status, 
        func.count(CaseReport.report_id)
    ).filter_by(
        assigned_officer_id=officer_id
    ).group_by(CaseReport.status).all()

    status_labels = [stat[0] for stat in case_stats]
    status_counts = [stat[1] for stat in case_stats]

    return render_template('officer/officer-dashboard.html', 
                           all_cases_count=all_cases_count, 
                           completed_cases_count=completed_cases_count,
                           urgent_cases_count=urgent_cases_count,
                           recent_cases_count=recent_cases_count,
                           recent_activities=recent_activities,
                           upcoming_deadlines=upcoming_deadlines,
                           status_labels=status_labels,
                           status_counts=status_counts)

@officers.route('/officer/assigned-cases')
@officer_required
def assignedCase():
    officer_id = session['officer_id']

    search_assigned = request.args.get('search_assigned', '')
    try:
        if search_assigned:
            all_cases_assigned = CaseReport.query.filter(
                CaseReport.assigned_officer_id == officer_id
            ).filter(
                or_(
                CaseReport.crime_type.ilike(f'%{search_assigned}%') | 
                CaseReport.location.ilike(f'%{search_assigned}%') |
                CaseReport.date.ilike(f'%{search_assigned}%') |
                CaseReport.time.ilike(f'%{search_assigned}%') |
                CaseReport.created_at.ilike(f'%{search_assigned}%') |
                CaseReport.status.ilike(f'%{search_assigned}%') |
                CaseReport.urgency.ilike(f'%{search_assigned}%')
                )
            ).all()
        else:
            all_cases_assigned = CaseReport.query.filter_by(assigned_officer_id=officer_id).all()
    except:
        current_app.logger.error("Database error:")
        
        flash("No report with the keyword.", "warning")
        
        return redirect(url_for('officers.assignedCase'))
        

    return render_template('officer/assigned-cases.html', all_cases_assigned=all_cases_assigned)

@officers.route('/officer/case-details/<int:report_id>', methods=['POST','GET'])
@officer_required
def caseDetails(report_id):
    try:
        report = CaseReport.query.get_or_404(report_id)

        if report is None:
                flash("Case details not found.", "warning")
                return redirect(url_for('officers.reports'))
        
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
    
@officers.route('/officer/status')
@officer_required
def caseStatus():
    officer_id = session['officer_id']

    search_case_status = request.args.get('search_case_status', '')
    try:
        if search_case_status:
            case_status = CaseReport.query.filter(
                CaseReport.assigned_officer_id == officer_id
            ).filter(
                or_(
                CaseReport.location.ilike(f'%{search_case_status}%') | 
                CaseReport.status.ilike(f'%{search_case_status}%') |
                CaseReport.date.ilike(f'%{search_case_status}%') |
                CaseReport.time.ilike(f'%{search_case_status}%') |
                CaseReport.crime_type.ilike(f'%{search_case_status}%') |
                CaseReport.created_at.ilike(f'%{search_case_status}%') |
                CaseReport.urgency.ilike(f'%{search_case_status}%')
                )
            ).all()
        else:
            case_status = CaseReport.query.filter_by(assigned_officer_id=officer_id).all()
    except:
        current_app.logger.error("Database error:")
        
        flash("No report with the keyword.", "warning")
        
        return redirect(url_for('officers.caseStatus'))
        

    return render_template('/officer/case-status.html', case_status=case_status)

@officers.route('/officer/status/<int:report_id>', methods=['POST'])
@officer_required
def updateCaseStatus(report_id):
    try:
        case = CaseReport.query.get_or_404(report_id)
        case_status = request.form.get('case_status')
        if case_status:
            case.status = case_status
            db.session.commit()
            flash(f'Success. Case status updated to {case_status}.', 'success')
        else:
            flash('Failed to update case status.', 'danger')
    except:
        current_app.logger.error("Database error:")
        
        flash("An error occurred. Please try again later.", "danger")
        
        return redirect(url_for('officers.caseStatus'))
    return redirect(url_for('officers.caseStatus'))

@officers.route('/officer/settled-cases')
@officer_required
def settledCase():
    officer_id = session['officer_id']
    search_settled_cases = request.args.get('search_settled_cases', '')
    try:
        if search_settled_cases:
            solved_cases = CaseReport.query.filter(
                CaseReport.assigned_officer_id == officer_id,
                CaseReport.status == 'Solved'
            ).filter(
                or_(
                CaseReport.location.ilike(f'%{search_settled_cases}%') | 
                CaseReport.status.ilike(f'%{search_settled_cases}%') |
                CaseReport.date.ilike(f'%{search_settled_cases}%') |
                CaseReport.time.ilike(f'%{search_settled_cases}%') |
                CaseReport.crime_type.ilike(f'%{search_settled_cases}%') |
                CaseReport.created_at.ilike(f'%{search_settled_cases}%') |
                CaseReport.urgency.ilike(f'%{search_settled_cases}%')
                )
            ).all()
        else:
            solved_cases = CaseReport.query.filter_by(assigned_officer_id=officer_id, status='Solved').all()
    except:
        current_app.logger.error("Database error:")
        
        flash("No report with the keyword.", "warning")
        
        return redirect(url_for('officers.settledCase'))
        
    return render_template('/officer/settled-cases.html', solved_cases=solved_cases)

@officers.route('/officer/officer-notification')
@officer_required
def officerNotification():
    return render_template('officer/officer-notification.html')

@officers.route('/officer/officer-setting')
@officer_required
def officerSetting():
    officer_id = session.get('officer_id')  
    officer_profile = Officers.query.get(officer_id)
    
    if not officer_profile:
        flash("Officer details not found", "error")
        return redirect(url_for('officers.officerSetting'))  
    
    return render_template('officer/officer-setting.html', officer=officer_profile)

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