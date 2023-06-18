
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file, sessions
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

from sqlalchemy import text

from ..utils.generate_model import Wibor

import json

@dataclass
class Interpolator:

    data_startowa: str
    okres: str
    punkty: list


dom = Blueprint('dom', __name__)

@dom.route('/domy')
def domy():
    '''
    select EXP(SUM(LOG(yourColumn))) As ColumnProduct from yourTable

    select date(substring(data_zakupu,7,4) || '-' || substring(data_zakupu,4,2) || '-' || substring(data_zakupu,1,2)) as miesiac from dom
    
    from @t t1
    inner join @t t2 on t1.id >= t2.id
    group by t1.id, t1.SomeNumt
    order by t1.id
    '''

    sql = '''
    with domek as (
    select date(substring(data_zakupu,7,4) || '-' || substring(data_zakupu,4,2) || '-01') as miesiac, wartosc from dom
    ),
    inflacja as (
    select date(substring(miesiac,1,7) || '-01') as miesiac, wartosc from inflacjamm
    ),
    cos as (
    select row_number() OVER (ORDER BY inflacja.miesiac) AS id, domek.miesiac, inflacja.miesiac, domek.wartosc, inflacja.wartosc from domek 
    left outer join inflacja
    on inflacja.miesiac >= domek.miesiac
    )
    select * from cos
    '''

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

    inflacja_dict = [{'miesiac': row.miesiac.strftime('%Y-%m'), 'wartosc': str(row.wartosc)} for row in inflacja]

    # convert the list of dictionaries to JSON
    inflacja_dumps = json.dumps(inflacja_dict)


    res = db.session.execute(text(sql2))

    #result_list = [{'id': row[0], 'domek_miesiac': row[1], 'inflacja_miesiac': row[2], 'domek_wartosc': row[3], 'inflacja_wartosc': row[4]} for row in res]

    result_list= [{'inflacja_miesiac': row[0], 'inflacja_wartosc': row[1], 'infl_kum': row[2], 'dom_wartosc': row[3], 'dom_real_wartosc': row[4]} for row in res]

    p = [('01/10/2029', 2.0), ('01/10/2044', 8.0), ('01/10/2060', 1.0)]
    w = ut.WiborInter('3M', dt.datetime.strptime("04/11/2019", '%d/%m/%Y'), 360, 10, p)

    return render_template('domy.html', inflacja=inflacja_dumps, results=json.dumps(result_list), wibor=w.json_data)


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

