
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file, sessions, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Dom, Zapytanie, InflacjaMM, Kredyt, Nadplata
from project import db
from wtforms import Form, BooleanField, StringField, PasswordField, SelectField, validators
from dateutil.relativedelta import relativedelta
import datetime as dt
from pandas.tseries.offsets import BDay
import pandas as pd
from dataclasses import dataclass
import utils.generate_model as ut
import utils.proc as proc
from sqlalchemy import text

from utils.generate_model import Wibor
from utils.inflacja import InflacjaMiesiac, Nieruchomosc

import json

@dataclass
class Interpolator:

    data_startowa: str
    okres: str
    punkty: list


dom = Blueprint('dom', __name__)


@dom.route('/favicon')
def favicon():
    return url_for('static', filename='favicon.ico')

@dom.route('/kredyt/<int:kredyt_id>', methods=['GET'])
@dom.route('/kredyt', methods=['GET', 'POST'])
@login_required
def kredyt(kredyt_id=None):

    edycja = False
    dane = ''

    if request.method == 'GET' and kredyt_id:
        # zbierz dane kredytu
        kr = Kredyt.query.filter_by(id=kredyt_id).first().as_dict()
        nadplaty =  [n.as_dict() for n in Nadplata.query.filter_by(kredyt_id=kredyt_id)]
        
        print(kr)
        print(nadplaty)


    if request.method == 'POST':

        if 'wartosc_nadplaty' in request.form:
            print(request.form['id'])
            print(request.values)

            kredyt_id = request.form['id']

            data_nadplaty = request.form['data_nadplaty']
            wartosc_nadplaty = request.form['wartosc_nadplaty']
            nd = Nadplata(data_nadplaty=dt.datetime.strptime(data_nadplaty, '%d/%m/%Y'),
                            wartosc=wartosc_nadplaty,
                            kredyt_id=kredyt_id)
            db.session.add(nd)
            db.session.commit()
            flash(f"nadplata dodana", 'ok')
        else:

            if 'dane' in request.form:
                # edycja 
                edycja = True
                dane = request.form['dane']
                print(dane)
            else:
                data_start = request.form['dataStart']
                kapital = request.form['kapital']
                marza = request.form['marza']
                okresy = request.form['okresy']
                rodzaj_wiboru = request.form['rodzajWiboru']
                rodzaj_rat = request.form['rodzajRat']

                if 'id' in request.form:
                    
                    try:

                        kr_id = request.form['id']

                        kr = Kredyt.query.filter_by(id=kr_id).first()
                        kr.data_uruchomienia = dt.datetime.strptime(data_start, '%d/%m/%Y')
                        kr.wartosc = kapital
                        kr.marza = marza
                        kr.okresy = okresy
                        kr.rodzaj_wiboru = rodzaj_wiboru
                        kr.rodzaj_rat = rodzaj_rat
                        db.session.commit()
                        flash("zedytowano", 'ok')
                        
                    except:
                        flash("cos poszlo nie tak przy edycji", 'error')

                    return redirect(url_for('dom.pokaz_kredyty'))
                else:

                    try:
                        kr = Kredyt(uzytkownik=current_user.name,
                                    data_uruchomienia=dt.datetime.strptime(data_start, '%d/%m/%Y'),
                                    wartosc=kapital,
                                    marza=marza,
                                    okresy=okresy,
                                    rodzaj_wiboru=rodzaj_wiboru,
                                    rodzaj_rat=rodzaj_rat)
                        db.session.add(kr)
                        db.session.commit()
                        flash(f"dodane {data_start}", 'ok')
                    except:
                        flash("cos poszlo nie tak przy dodawaniu", 'error')

    

    return render_template('kredyt.html', edycja = edycja, dane = dane)

@dom.route('/pokazkredyty', methods=['GET'])
@login_required
def pokaz_kredyty():

    kredyty = [k.as_dict() for k in Kredyt.query.all()]


    return render_template('pokazkredyty.html', kredyty=json.dumps(kredyty))


@dom.route('/mojkredyt', methods=['GET', 'POST'])
def mojkredyt():

    if request.method == 'POST':
        kapital = request.form['kapital']
    else:
        kapital = 460000



    marza = 2.99
    rodzaj_wiboru = '3M'
    data_start = '04/11/2021'
    okresy = 360
    liczba_wakacji = 0

    fin_data = {}
    fin_data['kapital'] = kapital
    fin_data['marza'] = marza
    fin_data['okresy'] = okresy
    fin_data['data_start'] = data_start

    prognoza = [('01/10/2029', 3.0), ('01/10/2040', 7.0), ('01/10/2044', 3.0), ('01/10/2160', 3.0)]

    w = ut.WiborInter(rodzaj_wiboru, dt.datetime.strptime(data_start, '%d/%m/%Y'), okresy, liczba_wakacji, prognoza)

    start_date = dt.datetime.strptime(data_start, '%d/%m/%Y')
    nadplaty = [{'dzien': '12-07-2023', 'kwota': 8000.00},
    {'dzien': '10-07-2023', 'kwota': 150.00},
    {'dzien':'06-07-2023', 'kwota':4500.00},
    {'dzien':'27-06-2023', 'kwota':1000.00},
    {'dzien':'16-06-2023', 'kwota':100.00},
    {'dzien':'22-05-2023', 'kwota':600.00},
    {'dzien':'13-04-2023', 'kwota':1500.00},
    {'dzien':'20-03-2023', 'kwota':1700.00},
    {'dzien':'20-02-2023', 'kwota':1000.00},
    {'dzien':'26-01-2023', 'kwota':1000.00},
    {'dzien':'16-12-2022', 'kwota':1000.00},
    {'dzien':'17-11-2022', 'kwota':1990.45},
    {'dzien':'14-10-2022', 'kwota':600.00},
    {'dzien':'05-05-2022', 'kwota':608.00},
    {'dzien':'02-05-2022', 'kwota':200.00},
    {'dzien':'25-04-2022', 'kwota':3000.00}]

    nadplata_start = dt.datetime.strptime('12/05/2024', '%d/%m/%Y')
    for o in range(240):
        dzien = (nadplata_start + relativedelta(months=o)).strftime('%d-%m-%Y')
        nadplaty.append({'dzien': dzien, 'kwota': 2000})

    for n in nadplaty:
        n['dzien'] = dt.datetime.strptime(n['dzien'], '%d-%m-%Y').strftime('%Y-%m-%d')



    dane_kredytu =  ut.generateFromWiborFileInter(w, kapital,
                                                   okresy,
                                                   dt.datetime.strptime(data_start, '%d/%m/%Y'), 
                                                   marza,
                                                   [],
                                                   nadplaty, 
                                                   False)
    
    inflacja = InflacjaMM.query.all()

    inflacja_dict = [{'miesiac': row.miesiac.strftime('%Y-%m'), 'wartosc': str(row.wartosc)} for row in inflacja if row.miesiac >= dt.datetime.strptime('2021-11', '%Y-%m')]

    print(f"inflacja : {inflacja_dict}")

    prognoza_inflacja = [('01/10/2029', 100.2), ('01/10/2044', 100.2), ('01/10/2160', 100.2)]

    wynik = proc.create_kredyt(dane_kredytu, 'stale')

    dzien_ostatniej_raty = max([dt.datetime.strptime(d['dzien'],'%Y-%m-%d') for d in wynik['raty']])

    inf = InflacjaMiesiac(dt.datetime.strptime(data_start, '%d/%m/%Y'), okresy,  liczba_wakacji, inflacja_dict, prognoza_inflacja)

    raty = {f"{n['dzien']}": n['rata'] for n in wynik["raty"]}
    nadplaty = {f"{n['dzien']}": n['kwota'] for n in wynik["nadplaty"]}

    inne = [{'dzien':'2021-11-04', 'kwota': 40000}]

    # koszty = {x: float(raty.get(x, 0)) + float(nadplaty.get(x, 0)) + float(inne.get(x, 0))  for x in sorted(list(set(raty).union(nadplaty).union(inne)))}
    
    koszty = {}
    for k in wynik["raty"]:
        miesiac = k['dzien'][0:7]
        if miesiac in koszty:
            koszty[miesiac] += float(k['rata'])
        else:
            koszty[miesiac] = float(k['rata'])
    for k in wynik["nadplaty"]:
        miesiac = k['dzien'][0:7]
        if miesiac in koszty:
            koszty[miesiac] += float(k['kwota'])
        else:
            koszty[miesiac] = float(k['kwota'])
    for k in inne:
        miesiac = k['dzien'][0:7]
        if miesiac in koszty:
            koszty[miesiac] += float(k['kwota'])
        else:
            koszty[miesiac] = float(k['kwota'])
  

    koszty_list = []
    for k in koszty.keys():
        koszty_list.append({'dzien':dt.datetime.strptime(k, '%Y-%m'), 'wartosc': koszty[k]})

    raty_list = []
    for k in raty.keys():
        raty_list.append({'dzien':dt.datetime.strptime(k, '%Y-%m-%d'), 'wartosc': raty[k]})

    kpo_list = [{'dzien':dt.datetime.strptime(data_start, '%d/%m/%Y'), 'wartosc': kapital}]
    for k in wynik["raty"]:
        kpo_list.append({'dzien':dt.datetime.strptime(k['dzien'], '%Y-%m-%d'), 'wartosc': k['K_po']})

    nom_kpo = [{'dzien': dt.datetime.strftime(k['dzien'], '%Y-%m'), 'wartosc': k['wartosc']} for k in kpo_list]
    

    real_koszty = inf.urealnij(koszty_list)
    real_raty = inf.urealnij(raty_list)
    real_kpo = inf.urealnij(kpo_list)

    nier_points = [{'dzien':start_date, 'wartosc': 500000}, {'dzien':dt.datetime.strptime('2056-01-01', '%Y-%m-%d'), 'wartosc': 1200000}]
    nier = Nieruchomosc(dt.datetime.strptime(data_start, '%d/%m/%Y'), okresy,  liczba_wakacji, nier_points, dzien_ostatniej_raty) 
    
    real_wartosc_nieruchomosc = inf.urealnij(nier.json_data)

    nom_koszty = [{'dzien': dt.datetime.strftime(r['dzien'], '%Y-%m'), 'wartosc': r['wartosc']} for r in koszty_list]
    nom_raty = [{'dzien': dt.datetime.strftime(r['dzien'], '%Y-%m'), 'wartosc': r['wartosc']} for r in raty_list]

    return render_template('mojkredyt.html', 
                           wibor=json.dumps(w.json_data),
                           wynik=json.dumps(wynik), 
                           fin_data = json.dumps(fin_data),
                           inflacja=json.dumps(inf.json_data),
                           real_koszty=json.dumps(real_koszty),
                           nom_koszty=json.dumps(nom_koszty),
                           real_raty=json.dumps(real_raty),
                           nom_raty=json.dumps(nom_raty),
                           nom_kpo=json.dumps(nom_kpo),
                           real_kpo=json.dumps(real_kpo),
                           nom_wartosc_nieruchomosc=json.dumps(nier.get_points()),
                           real_wartosc_nieruchomosc=json.dumps(real_wartosc_nieruchomosc))



@dom.route('/kiedy', methods=['GET', 'POST']) 
@login_required
def kiedywibor():

    if request.method == 'POST':
        dzien = request.get_json()['dzien']
        start_date = dt.datetime.strptime(dzien, '%d/%m/%Y')
        okresy = 10
        miesiace = []
        wibor = Wibor('3M')
        for i in range(okresy):
            dzien = start_date + relativedelta(months=3*i)
            dzienwibor = dzien - BDay(2)
            wibor_value = wibor.getWiborExact(dzienwibor)

            miesiace.append({'dzien':dzien.strftime('%d-%m-%Y'), 'dzienwibor': dzienwibor.strftime('%d-%m-%Y'), 'wibor': wibor_value})

  
        return json.dumps(miesiace)

    return render_template('kiedy.html')

@dom.route('/daty', methods=['GET', 'POST']) 
@login_required
def daty():


    df = pd.read_csv('project/static/plopln3m_d.csv', usecols=[0,1])
    result = df.to_json(orient="records")

    df3 = pd.read_csv('project/static/plopln3m_d.csv', usecols=[0,1], index_col=0)
    df3.index = pd.to_datetime(df3.index, format='%Y-%m-%d')

    min_day_wibor = df3.index.min()
    max_day_wibor = df3.index.max()

    a = df3.loc[max_day_wibor.strftime('%Y-%m-%d')][0]

    check_day = min_day_wibor
    iloscbl = 0
    while check_day <= max_day_wibor:
        d = check_day.dayofweek
        try:
            df3.loc[check_day.strftime('%Y-%m-%d')][0]
        except:
            if d in [0,1,2,3,4]:
                iloscbl += 1
                print(check_day)
        check_day = check_day + pd.DateOffset(1)
    
        
    print(iloscbl)
    print(max_day_wibor)
    print(max_day_wibor.dayofweek)


    return render_template('daty.html', datki=json.loads(result))

@dom.route("/logs", methods=['GET', 'POST'])
@login_required
def logs():
    
    zap = Zapytanie.query.all()

    resp = ""
    for z in zap:
        resp += f" <<< {z.user} at {z.created} >>> "


    return resp

