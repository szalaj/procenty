

from flask import Blueprint, render_template, current_app, flash, redirect, url_for, request, send_file, sessions, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
 
from obliczeniakredytowe import db

rrso = Blueprint('rrso', __name__)



@rrso.route('/rrso', methods=['GET', 'POST'])
@login_required
def rrso_main():
    print(current_app)
    print(request)
    return render_template('rrso/rrso.html')