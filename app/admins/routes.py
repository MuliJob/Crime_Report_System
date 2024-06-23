from flask import Blueprint, render_template, redirect, request, flash, session, url_for
from app.admins.models import Admin 
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.posts.models import Crime, Theft
from app.users.models import User

admins = Blueprint('admins', __name__)

# admin login
@admins.route('/admin/', methods=['GET', 'POST'])
def adminIndex():
    if request.method == 'POST':
        # get the value of field
        username = request.form.get('username')
        password = request.form.get('password')
        # check the value is not empty
        if username == '' and password == '':
            flash('Please fill all the field', category='danger')
            return redirect('/admin/')
        else:
            # login admin by username
            admins = Admin().query.filter_by(username=username).first()
            if admins and check_password_hash(admins.password,password):
                session['admin_id']=admins.id
                session['admin_name']=admins.username
                flash('Login Successfully', category='success')
                return redirect('/admin/dashboard')
            else:
                flash("Invalid Email and Password", category='danger')
                return redirect('/admin/')
    else:   
        return render_template('admin/index.html', 
        title='Admin Login')

@admins.route('/admin/dashboard')
def adminDashboard():
    user_count = User.query.count()
    crime_count = Crime.query.count()
    theft_count = Theft.query.count()
    #recovered_count = Recovered.query.count()
    
    # Fetch trend data for the graph (e.g., monthly counts)
    crime_trends = [30, 50, 70, 60, 90, 100, 120]  # Example data
    theft_trends = [20, 40, 60, 50, 80, 90, 110]   # Example data

    return render_template('admin/dashboard.html', user_count=user_count, crime_count=crime_count, theft_count=theft_count, crime_trends=crime_trends, theft_trends=theft_trends)

# change admin password
@admins.route('/admin/change-admin-password',methods=["POST","GET"])
def adminChangePassword():
    admin=Admin.query.get(1)
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if username == "" or password=="":
            flash('Please fill the field','danger')
            return redirect('/admin/change-admin-password')
        else:
            Admin().query.filter_by(username=username).update(dict(password=generate_password_hash(
                                password, 
                                method='pbkdf2:sha256')))
            db.session.commit()
            flash('Admin Password update successfully','success')
            return redirect('/admin/change-admin-password')
    else:
        return render_template('admin/admin-change-password.html',title='Admin Change Password',admin=admin)


@admins.route('/admin/reports')
def reports():
    crimes = Crime.query.all()
    thefts = Theft.query.all()
    
    return render_template('admin/reports.html', title='Reports Dashboard', crimes=crimes, thefts=thefts)

@admins.route('/admin/crime_details/<int:crime_id>')
def crimeDetails(crime_id):
    # Finding crime by id
    crime_details = Crime.query.filter_by(crime_id=crime_id).all()

    return render_template('admin/crime_details.html', crime_details=crime_details)

@admins.route('/admin/theft_details/<int:theft_id>')
def theftDetails(theft_id):
    #Finding theft by id 
    theft_details = Theft.query.filter_by(theft_id=theft_id).all()

    return render_template('admin/theft_details.html', theft_details=theft_details)

@admins.route('/admin/analytics')
def analytics():
    return render_template('admin/analytics.html', title='Analytics Dashboard')

@admins.route('/admin/dashboard')
def adminLogout():    
    if not session.get('admin_id'):
        return redirect('/admin/')
    if session.get('admin_id'):
        session['admin_id']=None
        session['admin_name']=None
        return redirect('/')
