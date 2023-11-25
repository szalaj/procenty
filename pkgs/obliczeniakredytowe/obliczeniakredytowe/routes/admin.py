
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file, sessions
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Dom, Zapytanie, InflacjaMM, Kredyt, Nadplata
from obliczeniakredytowe import db
import os
from sqlalchemy import text as sql_text
import csv
import pandas as pd
import json
import datetime as dt
from loguru import logger

from werkzeug.exceptions import HTTPException

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
                logger.info(f"Użytkownik {uzytkownik} zalogowany")
                return redirect(url_for('dom.start'))

    return render_template('admin/login.html')

@admin_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('rrso.rrso_main'))


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

@admin_bp.route('/status')
@login_required
def status():

    df = pd.read_sql(sql_text(f"SELECT data, wartosc, rodzaj FROM wibor"), con=db.engine.connect())


    # convert columns of df to list of dictionaries (one dict per row)
    dta = df.to_dict(orient='records')

    # conver df records into json 

    df_inflacjamm =pd.read_sql(sql_text(f"SElECT miesiac, wartosc FROM inflacjamm"), con=db.engine.connect(), parse_dates='miesiac')

    df_inflacjamm['miesiac'] = df_inflacjamm['miesiac'].dt.strftime('%Y-%m')

    dr_inflacja = df_inflacjamm.to_dict(orient='records')

    



    return render_template('admin/status.html', wibor=json.dumps(dta), inflacja=json.dumps(dr_inflacja))




def page_not_found(e):
    print('404')
    # note that we set the 404 status explicitly
    return render_template('admin/500_generic.html'), 404