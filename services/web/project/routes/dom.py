
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file, sessions
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Dom, Zapytanie
from project import db
from wtforms import Form, BooleanField, StringField, PasswordField, SelectField, validators
from dateutil.relativedelta import relativedelta
import datetime as dt
from pandas.tseries.offsets import BDay

import json

dom = Blueprint('dom', __name__)

@dom.route('/domy')
def domy():
    domy = Dom.query.all()
    r = ""
    for d in domy:
        r += d.data_zakupu
    return r


@dom.route('/kiedy', methods=['GET', 'POST']) 
@login_required
def kiedywibor():

    # form = KredytForm(request.form)
    # print(form.validate())
    message = ""
    if request.method == 'POST':
        dzien = request.get_json()['dzien']
        start_date = dt.datetime.strptime(dzien, '%d/%m/%Y')
        okresy = 10
        miesiace = []
        for i in range(okresy):
            dzien = start_date + relativedelta(months=3*i)
            dzienwibor = dzien - BDay(2)

            miesiace.append({'dzien':dzien.strftime('%d-%m-%Y'), 'dzienwibor': dzienwibor.strftime('%d-%m-%Y')})

  
        return json.dumps(miesiace)

    return render_template('formularz.html', message=message)


@dom.route("/logs", methods=['GET', 'POST'])
@login_required
def logs():
    
    zap = Zapytanie.query.all()

    resp = ""
    for z in zap:
        resp += f" <<< {z.user} at {z.created} >>> "


    return resp

