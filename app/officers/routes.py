from flask import Blueprint

officers = Blueprint('officers', __name__)

@officers.route('/officer/', methods=['GET', 'POST'])
def officerLogin():
  pass