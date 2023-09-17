
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file, session
from flask_login import login_user, logout_user, login_required, current_user
import requests
import re
import utils.generate_model
import pandas as pd
from io import BytesIO
import utils.proc
import datetime as dt
import utils.create_document
from werkzeug.utils import secure_filename
import datetime

from ..models import User, Dom, Zapytanie
from obliczeniakredytowe import db

import json


bp = Blueprint('bp', __name__)






@bp.route("/wibor", methods=['GET', 'POST'])
@login_required
def wibor():

    with requests.Session() as s:

        response6m = s.get('https://stooq.pl/q/d/l/?s=plopln6m&i=d')
    



        with open("./obliczeniakredytowe/static/plopln6m_d.csv", "w") as f:
            f.write(response6m.content.decode('utf-8'))

    # response3m = requests.get('https://stooq.pl/q/d/l/?s=plopln3m&i=d')
    
    # with open("./obliczeniakredytowe/static/plopln3m_d.csv", "w") as f:
    #     f.write(response3m.content.decode('utf-8'))
    
    return redirect(url_for('dom.pokaz_kredyty'))




