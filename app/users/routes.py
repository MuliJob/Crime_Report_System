from flask import Blueprint, render_template, redirect, session, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from app.users.models import User, Register
from app.posts.models import Crime, Theft
from app import db, api_key
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
    
    return render_template('signin.html')
    

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
    
    return render_template('signup.html')

@users.route('/users/register', methods=['GET', 'POST'])
def register():
    if  session.get('user_id'):
        return redirect('/users/dashboard')
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
                                    gender=gender)
            db.session.add(personal_details)
            db.session.commit()
            flash(f"Hello, {fullname}, welcome to the most secure website for reporting crimes", category='success')
            return redirect(url_for('users.user_dashboard'))

    return render_template('register.html')

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
    



@users.route('/users/dashboard', methods=['GET', 'POST'])
def user_dashboard(): 
    if not session.get('user_id'):
        return redirect('/users/signin')   
    url = f'https://newsapi.org/v2/everything?q=apple&from=2024-05-31&to=2024-05-31&sortBy=popularity&apiKey={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        news_data = response.json()
        articles = news_data.get('articles', [])
    except RequestException:
        flash("Error fetching news. Try connecting to internet", category='danger')
        articles = []

    return render_template('userdashboard.html', articles=articles)



@users.route('/users/history')
def history():
    user = current_user

    crimes = Crime.query.all()
    print(crimes)  # Print the list of crimes

    return render_template('history.html', crimes=crimes)

@users.route('/users/status')
def status():
    return render_template('status.html')

@users.route('/users/settings')
def settings():
    return render_template('settings.html')

@users.route('/users/change-password',methods=["POST","GET"])
def userChangePassword():
    if not session.get('user_id'):
        return redirect('/users/')
    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')
        if email == "" or password == "":
            flash('Please fill the field','danger')
            return redirect('/users/change-password')
        elif len(password) < 8:
            flash('Password should not be less than 8 characters', 'danger')
            return redirect('/users/change-password')
        else:
            users=User.query.filter_by(email=email).first()
            if users:
               password=generate_password_hash(
                                password, 
                                method='pbkdf2:sha256')
               User.query.filter_by(email=email).update(dict(password=password))
               db.session.commit()
               flash('Password Change Successfully','success')
               return redirect('/users/settings')
            else:
                flash('Invalid Email','danger')
                return redirect('/users/change-password')

    else:
        return render_template('change-password.html',title="Change Password")


