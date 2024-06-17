from flask import Blueprint, render_template, redirect, request, flash, session, url_for
from app.admins.models import Admin 
from werkzeug.security import check_password_hash, generate_password_hash
from app import db

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
    return render_template('admin/admin-dashboard.html')

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


@admins.route('/admin/dashboard')
def adminLogout():    
    if not session.get('admin_id'):
        return redirect('/admin/')
    if session.get('admin_id'):
        session['admin_id']=None
        session['admin_name']=None
        return redirect('/')
