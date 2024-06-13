from flask import render_template, redirect, url_for, request, flash, Blueprint
from . import db, api_key
from .models import User, Crime, Theft
from requests.exceptions import RequestException
import requests

views = Blueprint('views', __name__)


# Views
@views.route('/home')
def home_page():

    '''
    View root page function that returns the index page and its data
    '''
    return render_template('home.html')

@views.route('/about')
def about():
    return render_template('about.html')

@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        idno = request.form.get('idno')
        fullname = request.form.get('fullname')
        phonenumber = request.form.get('phonenumber')
        residence = request.form.get('residence')
        gender = request.form.get('gender')

        if len(idno) < 8 or len(idno) > 8:
            flash('Identification Number must be equal to or not more than 8 characters.', category='danger')
        elif len(fullname) < 4:
            flash('Full Name must be more than 4 characters.', category='danger')
        elif len(phonenumber) < 10:
            flash('Phone Number must be equal to 10 characters', category='danger')
        else:
            personal_details = User(idno=idno, 
                                    fullname=fullname, 
                                    phonenumber=phonenumber, 
                                    residence=residence, 
                                    gender=gender)
            db.session.add(personal_details)
            db.session.commit()
            flash(f"Hello, {fullname}, welcome to the most secure website for reporting crimes", category='success')
            return redirect(url_for('views.user_dashboard'))

    return render_template('register.html')

@views.route('/dashboard', methods=['GET', 'POST'])
def user_dashboard():
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

@views.route('/theft_report', methods=['GET', 'POST'])
def report_theft():   
    if request.method == 'POST':
        place_of_theft = request.form.get('place_of_theft')
        street_address = request.form.get('street_address')
        city = request.form.get('city')
        date_of_theft = request.form.get('date_of_theft')
        phone_number = request.form.get('phone_number')
        value = request.form.get('value')
        time_of_theft = request.form.get('time_of_theft')
        stolen_property = request.form.get('stolen_property')
        description = request.form.get('description')

        theft_report = Theft(place_of_theft=place_of_theft, 
                                street_address=street_address,
                                city=city, 
                                date_of_theft=date_of_theft,
                                phone_number=phone_number, 
                                value=value,
                                time_of_theft=time_of_theft, 
                                stolen_property=stolen_property,
                                description=description)
        db.session.add(theft_report)
        db.session.commit()
        flash(f"Your theft report was sent successfully", category='success')
        return redirect(url_for('user_dashboard'))
    return render_template('report_theft.html')


@views.route('/crime_report')
def report_crime():
    return render_template('report_crime.html')

@views.route('/history')
def history():
    return render_template('history.html')

@views.route('/status')
def status():
    return render_template('status.html')

@views.route('/settings')
def settings():
    return render_template('settings.html')

@views.route('/admin')
def admin_dashboard():
    return render_template('admin.html')