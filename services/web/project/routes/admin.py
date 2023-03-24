
from flask import Blueprint, render_template, flash, redirect, url_for, request, send_file, sessions
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Dom, Zapytanie
from project import db
admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
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

@admin_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('bp.main'))
