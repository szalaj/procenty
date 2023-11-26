
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file, session
from flask_login import login_user, logout_user, login_required, current_user
import requests
import re
import utils.generate_model
import pandas as pd
import io
from io import BytesIO
import utils.proc
import datetime as dt
import utils.create_document
from werkzeug.utils import secure_filename
from sqlalchemy import func 
import datetime

from ..models import User, Dom, Zapytanie, Wibor
from obliczeniakredytowe import db

import json


bp = Blueprint('bp', __name__)



def update_wibor(rodzaj:str, link:str):


    response = requests.get(link)    
    df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))


    max_wib = db.session.query(func.coalesce(func.max(Wibor.data),datetime.datetime(2000,1,1))).filter(Wibor.rodzaj==rodzaj).first()
    max_wib_str = dt.datetime.strftime(max_wib[0], '%Y-%m-%d')


    df_w= df[df['Data']>max_wib_str].loc[:, ['Data', 'Otwarcie']]
    df_w['rodzaj'] = rodzaj

    df_w= df_w.rename(columns={"Data": "data", "Otwarcie": "wartosc"})
    df_w.to_sql('wibor',con=db.engine, if_exists = 'append', index=False)




@bp.route("/wibor", methods=['GET', 'POST'])
@login_required
def wibor():



    update_wibor('wibor3m', 'https://stooq.pl/q/d/l/?s=plopln3m&i=d')

    update_wibor('wibor6m', 'https://stooq.pl/q/d/l/?s=plopln6m&i=d')

    update_wibor('stopa_ref', 'https://stooq.pl/q/d/l/?s=inrtpl.m&i=d')



    
    return redirect(url_for('rrso.rrso_main'))




