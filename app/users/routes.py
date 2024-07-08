import io
import os
from flask import Blueprint, current_app, render_template, redirect, send_from_directory, session, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from app.users.models import User, Register
from app.posts.models import Crime, Message
from app import db
from app.config import NEWS_API
from requests.exceptions import RequestException
import requests

users = Blueprint('users', __name__)

@users.route('/users/signin', methods=['GET', 'POST'])
def sign_in():
    if  session.get('user_id'):
        return redirect('/users/dashboard')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        
        if user:
            if check_password_hash(user.password, password):
                session['user_id']=user.id
                session['username']=user.username
                flash(f'Logged in successfully! Hello {username}', category='success')
                login_user(user, remember=True)
                return redirect(url_for('users.user_dashboard'))
            else: 
                flash('Incorrect password, try again.', category='danger')
        else:
            flash('Username does not exist.', category='danger')
    
    return render_template('user/signin.html')
    

@users.route('/users/signup', methods=['GET', 'POST'])
def sign_up():
    if  session.get('user_id'):
        return redirect('/users/dashboard')

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(username=username).first()
        email_address = User.query.filter_by(email=email).first()

        if user:
          flash('Username already exists.', category='danger')
        elif email_address:
          flash('Email already exists.', category='danger')
        elif len(username) < 2:
            flash('Username must be more than 1 characters.', category='danger')
        elif len(email) < 4:
            flash('Email must be more than 4 characters.', category='danger')
        elif password1 != password2:
            flash('Password don\'t match.', category='danger')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='danger')
        else:
            # add user to database
            new_user = User(username=username, 
                                email=email, 
                                password=generate_password_hash(
                                password1, 
                                method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('users.register'))
    
    return render_template('user/signup.html')

@users.route('/users/register', methods=['GET', 'POST'])
def register():
    if  session.get('user_id'):
        return redirect('/users/dashboard')
    
    user = current_user.id

    if request.method == 'POST':
        idno = request.form.get('idno')
        fullname = request.form.get('fullname')
        phonenumber = request.form.get('phonenumber')
        residence = request.form.get('residence')
        gender = request.form.get('gender')

        if len(idno) < 8 or len(idno) > 8:
            flash('Identification Number must be equal to 8 characters.', category='danger')
        elif len(fullname) < 4:
            flash('Full Name must be more than 4 characters.', category='danger')
        elif len(phonenumber) < 10 or len(phonenumber) > 10:
            flash('Invalid Phone number', category='danger')
        else:
            personal_details = Register(idno=idno, 
                                    fullname=fullname, 
                                    phonenumber=phonenumber, 
                                    residence=residence, 
                                    gender=gender,
                                    users_id=user)
            db.session.add(personal_details)
            db.session.commit()
            flash(f"Hello, {fullname}, Login to Access the Dashboard", category='success')
            return redirect(url_for('users.user_dashboard'))

    return render_template('user/register.html')

@users.route('/users/signout')
@login_required
def sign_out():
    if not session.get('user_id'):
        return redirect(url_for('users.sign_in'))
    
    if session.get('user_id'):
        session['user_id'] = None
        session['username'] = None
        flash('You have been logged out.', category='info')
        logout_user()
    return redirect(url_for('users.sign_in'))
    
# getting coordinates
@users.route('/save-coordinates', methods=['POST'])
def save_coordinates():
    data = request.get_json()
    session['latitude'] = data['latitude']
    session['longitude'] = data['longitude']
    return 'Coordinates saved', 200


@users.route('/users/dashboard', methods=['GET', 'POST'])
@login_required
def user_dashboard(): 
    user_id = session.get('user_id')
    latitude = session.get('latitude')
    longitude = session.get('longitude')
    print(latitude)
    print(longitude)
    if user_id:
        user = User.query.get(user_id)
        if user:
            login_user(user)   

            # fetching news data
            url = f'https://newsapi.org/v2/top-headlines?country=us&category=general&apiKey={NEWS_API}'

            try:
                response = requests.get(url)
                response.raise_for_status()
                news_data = response.json()
                articles = news_data.get('articles', [])
            except RequestException:
                flash("Error fetching news. Try connecting to internet", category='danger')
                articles = []

            return render_template('user/userdashboard.html', articles=articles, latitude=latitude, longitude=longitude)
        else:
            # If user not found, clear session and redirect to signin
            session.clear()
            return redirect('/users/signin')
    else:
        # If no user_id in session, redirect to signin
        return redirect('/users/signin')
        
@users.route('/users/history')
@login_required
def history():
    try:
        reporter = current_user.id

        # filter with current user login
        crimes = Crime.query.filter_by(reporter_id=reporter).all()

        return render_template('user/history.html', crimes=crimes)
    
    except Exception:
        flash('Unable to fetch your data. Please try again later.', 'danger')
        return render_template('user/history.html', crimes=[])


@users.route('/users/recovered-items')
@login_required
def recovered():
    try:
        recovered_crimes = Crime.query.filter_by(crime_status='Recovered').all()
    except:
        flash("An error occurred while fetching crime details. Please try again later.", "error")
        # Redirect to a safe page, like the admin dashboard
        return redirect(url_for('users.recovered'))
    
    return render_template('user/recovered_items.html', recovered_crimes=recovered_crimes)

# DOWNLOADING P3 FORM
@users.route('/users/downloads', methods=['GET', 'POST'])
@login_required
def download():
    if request.method == 'POST':
        # Handle the download request
        filename = "P3.pdf"  # Replace with your actual filename
        directory = os.path.join(current_app.root_path, 'static', 'files')
        
        # Check if file exists
        if os.path.exists(os.path.join(directory, filename)):
            return send_from_directory(directory, filename, as_attachment=True)
        else:
            # Handle file not found error
            flash('Unable to download file', 'warning')
            return redirect(url_for('users.download'))
        
    return render_template('user/downloads.html')

# displaying crime details when button is clicked
@users.route('/users/crime-details/<int:crime_id>')
@login_required
def crime_details(crime_id):
    try:
        # Finding crime by id
        crime_details = Crime.query.filter_by(crime_id=crime_id).all()
        

    except:
        flash("An error occurred while fetching crime details. Please try again later.", "error")
        # Redirect to a safe page, like the admin dashboard
        return redirect(url_for('users.history'))

    return render_template('user/crime-details.html', crime_details=crime_details, )

@users.route('/users/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not session.get('user_id'):
        return redirect('/users/dashboard')

    users_id = session.get('user_id')
    
    try:
        user = User.query.get(users_id)
        user_details = Register.query.filter_by(users_id=users_id).first()
        
        if not user_details:
            user_details = Register(users_id=users_id)
            db.session.add(user_details)
            db.session.commit()

    except Exception as e:
        flash('An error has occurred. Please try again later', 'danger')
        return redirect(url_for('users.settings'))

    if request.method == 'POST':
        if 'update_profile' in request.form:
            user_details.fullname = request.form.get('fullname')
            user_details.phonenumber = request.form.get('phonenumber')
            user_details.residence = request.form.get('residence')
            user_details.gender = request.form.get('gender')

            try:
                db.session.commit()
                flash('Profile updated successfully', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred while updating profile: {str(e)}', 'danger')

        elif 'change_password' in request.form:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not check_password_hash(user.password, current_password):
                flash('Current password is incorrect', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match', 'danger')
            else:
                user.password = generate_password_hash(new_password)
                try:
                    db.session.commit()
                    flash('Password changed successfully', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'An error occurred while changing password: {str(e)}', 'danger')

        return redirect(url_for('users.settings'))
        
    return render_template('user/settings.html',title="User Dashboard",user=user, user_details=user_details)

# notifications
@users.route('/users/notification')
@login_required
def notification():
    try:
        sender = current_user.id
        user_message = Message.query.filter_by(sender_id=sender).all()

    except:
        # Log the error
        current_app.logger.error("Database error occurred:")
        
        # Flash an error message to the user
        flash("No report with the keyword.", "warning")
        
        # Redirect to a safe page, like the admin dashboard
        return redirect(url_for('users.notification'))
    return render_template('user/notification.html', user_message=user_message)



