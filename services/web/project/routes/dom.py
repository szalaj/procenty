
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file, sessions, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Dom, Zapytanie, InflacjaMM
from project import db
from wtforms import Form, BooleanField, StringField, PasswordField, SelectField, validators
from dateutil.relativedelta import relativedelta
import datetime as dt
from pandas.tseries.offsets import BDay
import pandas as pd
from dataclasses import dataclass
import project.utils.generate_model as ut
import project.utils.proc as proc
from sqlalchemy import text

from ..utils.generate_model import Wibor
from project.utils.inflacja import InflacjaMiesiac, Nieruchomosc

import json

@dataclass
class Interpolator:

    data_startowa: str
    okres: str
    punkty: list


dom = Blueprint('dom', __name__)



@dom.route('/favicon.ico')
def favicon():
    return url_for('static', filename='favicon.ico')

@dom.route('/kredyt')
def kredyt():

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

    prognoza = [('01/10/2029', 3.0), ('01/10/2044', 3.0), ('01/10/2160', 3.0)]

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

    # for o in range(okresy):
    #     dzien = (start_date + relativedelta(months=o)).strftime('%Y-%m-%d')
    #     nadplaty.append({'dzien': dzien, 'kwota': 2000})
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

    inf = InflacjaMiesiac(dt.datetime.strptime(data_start, '%d/%m/%Y'), okresy,  liczba_wakacji, inflacja_dict, prognoza_inflacja)

    print(f"inflacja przetrawiona {inf.json_data}")

    #raty = [{'dzien':  dt.datetime.strptime(r['dzien'], '%Y-%m-%d'), 'wartosc': r['rata']} for r in wynik['raty']]
    raty = {f"{n['dzien']}": n['rata'] for n in wynik["raty"]}
    kpo = {f"{n['dzien']}": n['K_po'] for n in wynik["raty"]}
    nadplaty = {f"{n['dzien']}": n['kwota'] for n in wynik["nadplaty"]}
    inne = {'2021-11-04': 50000}

    koszty = {x: float(raty.get(x, 0)) + float(nadplaty.get(x, 0)) + float(inne.get(x, 0))  for x in set(raty).union(nadplaty).union(inne)}
    #raty = {x: float(raty.get(x, 0)) for x in set(raty)}

    koszty_list = []
    for k in koszty.keys():
        koszty_list.append({'dzien':dt.datetime.strptime(k, '%Y-%m-%d'), 'wartosc': koszty[k]})

    raty_list = []
    for k in raty.keys():
        raty_list.append({'dzien':dt.datetime.strptime(k, '%Y-%m-%d'), 'wartosc': raty[k]})

    kpo_list = []
    for k in wynik["raty"]:
        kpo_list.append({'dzien':dt.datetime.strptime(k['dzien'], '%Y-%m-%d'), 'wartosc': k['K_po']})

    real_koszty = inf.urealnij(koszty_list)
    real_raty = inf.urealnij(raty_list)
    real_kpo = inf.urealnij(kpo_list)

    nier_points = [{'dzien':start_date, 'wartosc': 500000}, {'dzien':dt.datetime.strptime('2056-01-01', '%Y-%m-%d'), 'wartosc': 1200000}]
    nier = Nieruchomosc(dt.datetime.strptime(data_start, '%d/%m/%Y'), okresy,  liczba_wakacji, nier_points) 
    
    real_wartosc_nieruchomosc = inf.urealnij(nier.json_data)

    nom_koszty = [{'dzien': dt.datetime.strftime(r['dzien'], '%Y-%m'), 'wartosc': r['wartosc']} for r in koszty_list]
    nom_raty = [{'dzien': dt.datetime.strftime(r['dzien'], '%Y-%m'), 'wartosc': r['wartosc']} for r in raty_list]

    return render_template('kredyt.html', 
                           wibor=json.dumps(w.json_data),
                           wynik=json.dumps(wynik), 
                           fin_data = json.dumps(fin_data),
                           inflacja=json.dumps(inf.json_data),
                           real_koszty=json.dumps(real_koszty),
                           nom_koszty=json.dumps(nom_koszty),
                           real_raty=json.dumps(real_raty),
                           nom_raty=json.dumps(nom_raty),
                           real_kpo=json.dumps(real_kpo),
                           nom_wartosc_nieruchomosc=json.dumps(nier.get_points()),
                           real_wartosc_nieruchomosc=json.dumps(real_wartosc_nieruchomosc))


@dom.route('/domy')
def domy():


    sql2 = '''
    with domek as (
    select date(substring(data_zakupu,7,4) || '-' || substring(data_zakupu,4,2) || '-01') as miesiac, wartosc from dom
    ),
    inflacja as (
    select date(substring(miesiac,1,7) || '-01') as miesiac, wartosc from inflacjamm
    ),
    cos as (
    select 
        domek.miesiac as domek_miesiac, 
        inflacja.miesiac as inflacja_miesiac, 
        domek.wartosc as domek_wartosc, 
        CASE WHEN domek.miesiac=inflacja.miesiac THEN 1 ELSE inflacja.wartosc/100.0 END as inflacja_wartosc
    from domek 
    left outer join inflacja
    on inflacja.miesiac >= domek.miesiac
    ),
    wartosci as (
    select t1.inflacja_miesiac, t1.inflacja_wartosc, EXP(SUM(LN(t2.inflacja_wartosc))) as infl_kum, max(t1.domek_wartosc) as domek_wartosc
    from cos t1
    inner join cos t2
    on t1.inflacja_miesiac >= t2.inflacja_miesiac
    group by t1.inflacja_miesiac, t1.inflacja_wartosc
    order by t1.inflacja_miesiac
    )
    select inflacja_miesiac, inflacja_wartosc, infl_kum, domek_wartosc, domek_wartosc/infl_kum as dom_real_wartosc
    from wartosci
    
    '''

    domy = Dom.query.all()
    
    inflacja = InflacjaMM.query.all()

    inflacja_dict = [{'miesiac': row.miesiac.strftime('%Y-%m'), 'wartosc': str(row.wartosc)} for row in inflacja if row.miesiac >= dt.datetime.strptime('2021-11', '%Y-%m')]

    # convert the list of dictionaries to JSON
    inflacja_dumps = json.dumps(inflacja_dict)


    res = db.session.execute(text(sql2))

    #result_list = [{'id': row[0], 'domek_miesiac': row[1], 'inflacja_miesiac': row[2], 'domek_wartosc': row[3], 'inflacja_wartosc': row[4]} for row in res]

    result_list= [{'inflacja_miesiac': row[0], 'inflacja_wartosc': row[1], 'infl_kum': row[2], 'dom_wartosc': row[3], 'dom_real_wartosc': row[4]} for row in res]

    p = [ ('01/10/2044', 6.0), ('01/10/2052', 2.0) ,('01/10/2060', 10.0)]
    w = ut.WiborInter('3M', dt.datetime.strptime("04/11/2019", '%d/%m/%Y'), 360, 10, p)

    dane_kredytu =  ut.generateFromWiborFileInter(w, 400000, 200, dt.datetime.strptime("04/11/2019", '%d/%m/%Y'), 1, dt.datetime.strptime("04/11/2049", '%d/%m/%Y'), '3M', [], False, False)
    wynik = proc.create_kredyt(dane_kredytu, 'malejace')

    return render_template('domy.html', inflacja=inflacja_dumps, results=json.dumps(result_list), wibor=w.json_data, wynik=json.dumps(wynik))


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

