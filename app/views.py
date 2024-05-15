from flask import render_template, redirect, url_for
from app import app

# Views
@app.route('/')
@app.route('/home')
def home_page():

    '''
    View root page function that returns the index page and its data
    '''
    return render_template('base.html')

@app.route('/signin')
def sign_in():
    return render_template('signin.html')

@app.route('/signup')
def sign_up():
    return render_template('signup.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/signout')
def sign_out():
    return redirect(url_for("index"))