from flask import render_template, redirect, url_for, request, flash
from app import app, db
from app.models import User, Register
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user


# Views
@app.route('/')
@app.route('/home')
def home_page():

    '''
    View root page function that returns the index page and its data
    '''
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Register.query.filter_by(username=username).first()
        
        if user:
            if check_password_hash(user.password, password):
                flash(f'Logged in successfully! Welcome {username}', category='success')
                return redirect(url_for('user_dashboard'))
            else: 
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')
    
    

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = Register.query.filter_by(username=username).first()

        if user:
            flash('Username already exists.', category='error')
        elif len(username) < 2:
            flash('Username must be more than 1 characters.', category='error')
        elif len(email) < 4:
            flash('Email must be more than 4 characters.', category='error')
        elif password1 != password2:
            flash('Password don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # add user to database
            new_user = Register(username=username, 
                                email=email, 
                                password=generate_password_hash(
                                password1, 
                                method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for('register'))
        

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        idno = request.form.get('idno')
        fullname = request.form.get('fullname')
        phonenumber = request.form.get('phonenumber')
        residence = request.form.get('residence')
        gender = request.form.get('gender')

        if len(idno) < 8:
            flash('Identification Number must be equal to 8 characters.', category='error')
        elif len(fullname) < 4:
            flash('Full Name must be more than 4 characters.', category='error')
        elif len(phonenumber) < 10:
            flash('Phone Number must be equal to 10 characters', category='error')
        else:
            personal_details = User(idno=idno, 
                                    fullname=fullname, 
                                    phonenumber=phonenumber, 
                                    residence=residence, 
                                    gender=gender)
            db.session.add(personal_details)
            db.session.commit()
            flash(f"Welcome, {fullname}")
            return redirect(url_for('user_dashboard'))
    else:
        flash('Failed to complete registration! Please try again later...', category='error')
        return render_template('register.html')

@app.route('/signout')
@login_required
def sign_out():
    logout_user()
    return render_template('sign_in')

@app.route('/dashboard')
def user_dashboard():
    return render_template('userdashboard.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')