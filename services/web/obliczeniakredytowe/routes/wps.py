
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






@bp.route("/wibor", methods=['GET', 'POST'])
@login_required
def wibor():


    # response6m = requests.get('https://stooq.pl/q/d/l/?s=plopln6m&i=d')


    # with open("./obliczeniakredytowe/static/plopln6m_d.csv", "w") as f:
    #     f.write(response6m.content.decode('utf-8'))

    # response3m = requests.get('https://stooq.pl/q/d/l/?s=plopln3m&i=d')
    
    # with open("./obliczeniakredytowe/static/plopln3m_d.csv", "w") as f:
    #     f.write(response3m.content.decode('utf-8'))


    response3m = requests.get('https://stooq.pl/q/d/l/?s=plopln3m&i=d')    

    df = pd.read_csv(io.StringIO(response3m.content.decode('utf-8')))


    max_3m = db.session.query(func.coalesce(func.max(Wibor.data),datetime.datetime(2000,1,1))).filter(Wibor.rodzaj=='wibor3m').first()

    print(max_3m)

    # stworz df
    # 
    # wybierz z df rekordy z data wieksza niz max(tabela)
    # 
    # zapisz te rekordy do tabeli    
    
    return redirect(url_for('dom.pokaz_kredyty'))




