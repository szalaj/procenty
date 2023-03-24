
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file, sessions
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Dom, Zapytanie
from project import db
from wtforms import Form, BooleanField, StringField, PasswordField, SelectField, validators

dom = Blueprint('dom', __name__)

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


@dom.route('/domy')
def domy():
    domy = Dom.query.all()
    r = ""
    for d in domy:
        r += d.data_zakupu
    return r


@dom.route('/kiedy')
@login_required
def kiedywibor():

    return "jesteś szalona"



@dom.route("/logs", methods=['GET', 'POST'])
@login_required
def logs():
    
    zap = Zapytanie.query.all()

    resp = ""
    for z in zap:
        resp += f" <<< {z.user} at {z.created} >>> "


    return resp

