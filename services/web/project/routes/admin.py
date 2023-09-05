
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file, sessions
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Dom, Zapytanie, InflacjaMM, Kredyt, Nadplata
from project import db
import os
import csv

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('bp.main'))
    if request.method == 'POST':

        uzytkownik = str(request.form['uzytkownik'])
        haslo = str(request.form['haslo'])

        u = User.query.filter_by(name=uzytkownik).first()
        if u:
            if u.check_password(haslo):
                login_user(u)
                return redirect(url_for('dom.start'))

    return render_template('admin/login.html')

@admin_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('dom.start'))


@admin_bp.route('/backup')
@login_required
def backup():
    kredyty = [k.as_dict() for k in Kredyt.query.all()]
    nadplaty = [k.as_dict() for k in Nadplata.query.all()]

    

    data_file = open('backup/kredyty_backup.csv', 'w')
 
    # create the csv writer object
    csv_writer = csv.writer(data_file)
    
    # Counter variable used for writing
    # headers to the CSV file
    count = 0
    
    for emp in kredyty:
        if count == 0:
    
            # Writing headers of CSV file
            header = emp.keys()
            csv_writer.writerow(header)
            count += 1
    
        # Writing data of CSV file
        csv_writer.writerow(emp.values())
    
    data_file.close()

    data_file = open('backup/nadplaty_backup.csv', 'w')
 
    # create the csv writer object
    csv_writer = csv.writer(data_file)
    
    # Counter variable used for writing
    # headers to the CSV file
    count = 0
    
    for emp in nadplaty:
        if count == 0:
    
            # Writing headers of CSV file
            header = emp.keys()
            csv_writer.writerow(header)
            count += 1
    
        # Writing data of CSV file
        csv_writer.writerow(emp.values())
    
    data_file.close()
    flash('backup zrobiony')
    return redirect(url_for('dom.pokaz_kredyty'))

