
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file, session
from flask_login import login_user, logout_user, login_required, current_user
import sqlite3
from wtforms import Form, BooleanField, StringField, PasswordField, SelectField, validators
import requests
import sqlite3
import json
import re
import project.utils.generate_model
import pandas as pd
from io import BytesIO
import project.utils.proc
import datetime as dt
import project.utils.create_document
from werkzeug.utils import secure_filename
import datetime

from .models import User, Dom, Zapytanie
from project import db

bp = Blueprint('bp', __name__)

def get_db_connection():
    conn = sqlite3.connect('./project/database.db')
    conn.row_factory = sqlite3.Row
    return conn


    

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('bp.main'))
    if request.method == 'POST':

        uzytkownik = str(request.form['uzytkownik'])
        haslo = str(request.form['haslo'])

        u = User.query.filter_by(name=uzytkownik, password=haslo).first()
        if u:
            login_user(u)
            return redirect(url_for('bp.main'))

    return render_template('login.html')

@bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('bp.main'))



@bp.route("/formularz", methods=['GET', 'POST'])
@login_required
def formularz():

    form = KredytForm(request.form)
    print(form.validate())
    message = ""
    if request.method == 'POST' and form.validate():
        print('validate')
        name = form.name.data
        flash('Thanks for registering')
        return redirect(url_for('bp.main'))
    
    

    return render_template('formularz.html', form=form, message=message)
    


@bp.route("/", methods=['GET', 'POST'])
@login_required
def main():

    df3 = pd.read_csv('project/static/plopln3m_d.csv', usecols=[0,1], index_col=0)
    df3.index = pd.to_datetime(df3.index, format='%Y-%m-%d')

    df6 = pd.read_csv('project/static/plopln6m_d.csv', usecols=[0,1], index_col=0)
    df6.index = pd.to_datetime(df6.index, format='%Y-%m-%d')

    max_day_wibor3m = df3.index.max()
    max_day_wibor6m = df6.index.max()

    tech_data = {'max_day_wibor3m': max_day_wibor3m.strftime('%d-%m-%Y'),
            'max_day_wibor6m': max_day_wibor6m.strftime('%d-%m-%Y')}

    

    if request.method == 'POST':

        error = None

        try:
            marza_temp = re.search("^[\d\.\,\s]+(?=%?$)",request.form['marza']).group()
            marza_temp = marza_temp.replace(',','.')
        except:
            marza_temp = request.form['marza']
        

        form_data = {"kapital1":request.form['kapital1'],
                    "kapital2":request.form['kapital2'],
                    "kapital3":request.form['kapital3'],
                    "dataStart1":request.form['dataStart1'],
                    "dataStart2":request.form['dataStart2'],
                    "dataStart3":request.form['dataStart3'],
                    "dataUmowa":request.form['dataUmowa'],
                    "okresy":request.form['okresy'],
                    "marza":marza_temp,
                    "dataZamrozenia":request.form['dataZamrozenia'],
                    "rodzajWiboru":request.form['rodzajWiboru'],
                    "rodzajRat":request.form['rodzajRat']}

        if 'checkTransza2' in request.form:
            form_data['checkTr2'] = True


        if 'checkTransza3' in request.form:
            form_data['checkTr3'] = True

        tech_data['form_data'] = form_data

        try:
            kapital1 = float(form_data['kapital1'])
            dataStart1 = str(form_data['dataStart1'])
            dataUmowa = str(form_data['dataUmowa'])
            okresy = int(form_data['okresy'])
            
            
        
            marza = float(marza_temp)

            rodzajWiboru = str(form_data['rodzajWiboru'])
            rodzajRat = str(form_data['rodzajRat'])
            dataZamrozenia = str(form_data['dataZamrozenia'])


            data_start1 = dt.datetime.strptime(dataStart1, '%d/%m/%Y')
            data_zamrozenia = dt.datetime.strptime(dataZamrozenia, '%d/%m/%Y')
            data_umowa = dt.datetime.strptime(dataUmowa, '%d/%m/%Y')

            transze = []

            if 'checkTransza2' in request.form:
                kapital2 = float(form_data['kapital2'])
                dataStart2 = str(form_data['dataStart2'])
                data_start2 = dt.datetime.strptime(dataStart2, '%d/%m/%Y')

                transze.append({'dzien': data_start2, 'wartosc':kapital2 })

            if 'checkTransza3' in request.form:
                kapital3 = float(form_data['kapital3'])
                dataStart3 = str(form_data['dataStart3'])
                data_start3 = dt.datetime.strptime(dataStart3, '%d/%m/%Y')

                transze.append({'dzien': data_start3, 'wartosc':kapital3 })


            

            if data_zamrozenia > max_day_wibor3m if rodzajWiboru=='3M' else data_zamrozenia > max_day_wibor6m:
                error = "Data zamrożenia wiboru większa niż dostępne dane."
                flash('m')
                return render_template('wykres.html', error=error, tech_data=tech_data)




        except:
            error = "Wypełnij poprawnie formularz"
            flash('m')
            return render_template('wykres.html', error=error, tech_data=tech_data)

        

        dane_kredytu =  project.utils.generate_model.generateFromWiborFile(kapital1, okresy, data_start1, marza, data_zamrozenia, rodzajWiboru, transze, False)

        wibor = project.utils.generate_model.Wibor(rodzajWiboru)
        wibor_start = wibor.getWibor(data_umowa)
        stala_stopa_uruch = round(wibor_start + marza,2)
        wibor_zamrozony = dane_kredytu['wibor_zamrozony']

        
        

        dane_kredytu_alt =  project.utils.generate_model.generateFromWiborFile(kapital1, okresy, data_start1, stala_stopa_uruch, data_zamrozenia, rodzajWiboru, transze, True)


        wynik = project.utils.proc.create_kredyt(dane_kredytu, rodzajRat)
        wynik2 = project.utils.proc.create_kredyt(dane_kredytu_alt, rodzajRat)

        fin_data = {}
        fin_data['dane'] = wynik
        fin_data['dane2'] = wynik2

        fin_data['data_zamrozenia'] = data_zamrozenia.strftime('%d/%m/%Y')
        fin_data['wibor_start'] = wibor_start
        fin_data['wibor_zamrozony'] = wibor_zamrozony

        
        fin_data['stala_stopa_uruch'] = round(wibor_start + marza,2)

        

        zap = Zapytanie(user=current_user.name, created=datetime.datetime.utcnow)
        db.session.add(zap)
        db.session.commit()

        
        return render_template('wykres.html', tech_data=tech_data, fin_data=fin_data)



    return render_template('wykres.html', tech_data=tech_data)


@bp.route("/doc", methods=['GET', 'POST'])
@login_required
def get_doc():

    if request.method == 'POST':
        
        dane = request.get_json()
        document = project.utils.create_document.create_document(dane)
        
        f = BytesIO()
        # do staff with document
        document.save(f)
        f.seek(0)

        return send_file(
            f,
            mimetype='application/msword',
            as_attachment=True, 
            download_name   ='report.docx'
        )

@bp.route("/wibor", methods=['GET', 'POST'])
@login_required
def wibor():

    response6m = requests.get('https://stooq.pl/q/d/l/?s=plopln6m&i=d')
    
    with open("./project/static/plopln6m_d.csv", "wb") as f:
        f.write(response6m.content)

    response3m = requests.get('https://stooq.pl/q/d/l/?s=plopln3m&i=d')
    
    with open("./project/static/plopln3m_d.csv", "wb") as f:
        f.write(response3m.content)
    
    return redirect(url_for('bp.main'))


@bp.route("/logs", methods=['GET', 'POST'])
@login_required
def logs():
    
    zap = Zapytanie.query.all()

    resp = ""
    for z in zap:
        resp += z.user

    print(resp)
    return resp


@bp.route('/domy')
def dom():
    domy = Dom.query.all()
    r = ""
    for d in domy:
        r += d.data_zakupu
    return r


class KredytForm(Form):

    kapital1 = StringField('Kapitał - Transza 1.', [validators.Length(min=1, max=25)], description="Ile?")
    kapital2 = StringField('Kapitał - Transza 2.', [validators.Length(min=1, max=25)], description="Ile?")
    kapital3 = StringField('Kapital - Transza 3.', [validators.Length(min=1, max=25)], description="Ile?")
    dataStart1 = StringField('Data uruchomienia 1', [validators.Length(min=1, max=25)], description="DD/MM/YYYY")
    dataStart2 = StringField('Data uruchomienia 2', [validators.Length(min=1, max=25)], description="DD/MM/YYYY")
    dataStart3 = StringField('Data uruchomienia 3', [validators.Length(min=1, max=25)], description="DD/MM/YYYY")
    dataUmowa = StringField('Data podpisania umowy', [validators.Length(min=1, max=25)], description="DD/MM/YYYY")
    okresy = StringField('Ilość miesięcy', [validators.Length(min=1, max=25)], description="a")
    marza = StringField('Marża', [validators.Length(min=1, max=25)], description="%")
    dataZamrozenia = StringField('Data zamrozenia', [validators.Length(min=1, max=25)], description="DD/MM/YYYY")
    rodzajWiboru = SelectField('Rodzaj wiboru', choices=[('3M', '3M'), ('6M', '6M')])
    rodzajRat = SelectField('Rodzaj rat', choices=[('stale', 'stałe'), ('malejace', 'malejące')])
