
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file, sessions
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Dom, Zapytanie
from project import db
from wtforms import Form, BooleanField, StringField, PasswordField, SelectField, validators

from ..forms import KredytForm

dom = Blueprint('dom', __name__)

@dom.route('/domy')
def domy():
    domy = Dom.query.all()
    r = ""
    for d in domy:
        r += d.data_zakupu
    return r

# https://www.digitalocean.com/community/tutorials/how-to-use-and-validate-web-forms-with-flask-wtf
@dom.route('/kiedy')
@login_required
def kiedywibor():

    form = KredytForm(request.form)
    print(form.validate())
    message = ""
    if request.method == 'POST' and form.validate():
        print('validate')
        name = form.name.data
        flash('Thanks for registering')
        return redirect(url_for('bp.main'))
    
    

    return render_template('formularz.html', form=form, message=message)


@dom.route("/logs", methods=['GET', 'POST'])
@login_required
def logs():
    
    zap = Zapytanie.query.all()

    resp = ""
    for z in zap:
        resp += f" <<< {z.user} at {z.created} >>> "


    return resp

