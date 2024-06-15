from flask import Blueprint, render_template


main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home_page():

    '''
    View root page function that returns the index page and its data
    '''
    return render_template('home.html')

@main.route('/about')
def about():
    return render_template('about.html')