from flask import render_template, redirect, url_for, request, flash, session
from app import app
from flask_login import login_user, current_user, logout_user, login_required



# Views
@app.route('/')
@app.route('/home')
def home_page():

    '''
    View root page function that returns the index page and its data
    '''
    return render_template('home.html')

@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    
    return render_template('signin.html')
    

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    return render_template('signup.html')
        

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/signout')
def sign_out():
    logout_user()
    return redirect(url_for("home_page"))

@app.route('/dashboard')
def user_dashboard():
    
    return render_template('userdashboard.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')