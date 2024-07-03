from flask import Blueprint, flash, redirect, render_template, request, url_for
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

from app.officers.models import Officers

officers = Blueprint('officers', __name__)


@officers.route('/officer/register', methods=['GET', 'POST'])
def officerRegister():
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
            # add user to database
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

@officers.route('/officer/login', methods=['GET', 'POST'])
def officerLogin():
  return render_template('officer/login.html')