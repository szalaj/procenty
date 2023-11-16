

from flask import Blueprint, render_template, current_app, flash, redirect, url_for, request, send_file, sessions, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
import datetime as dt
from obliczeniakredytowe import db

rrso = Blueprint('rrso', __name__)



@rrso.route('/rrso', methods=['GET', 'POST'])
@login_required
def rrso_main():

    if request.method == 'POST':

        # data umowy
        data_umowy = request.form['data_umowy']
        print(data_umowy)

        try:
            data_umowy = dt.datetime.strptime(data_umowy, '%d/%m/%Y')
        except:
            flash('Niepoprawny format daty podpisania umowy. Poprawny format DD/MM/RRRR', 'error')

        # calkowita kwota kredytu
        calkowita_kwota = request.form['calkowita_kwota']

        try:
            calkowita_kwota = float(calkowita_kwota)
            if calkowita_kwota <= 0:
                raise Exception
        except:
            flash('Całkowita kwota kredytu musi być większa od 0', 'error')

        # Kwota udzielonego kredytu
        udzielona_kwota = request.form['udzielona_kwota']

        try:
            udzielona_kwota = float(udzielona_kwota)
            if udzielona_kwota <= 0:
                raise Exception
        except:
            flash('Kwota udzielonego kredytu musi być większa od 0', 'error')

        # Okresy
        okresy = request.form['okresy']

        try:
            okresy = float(okresy)
            if okresy <= 0:
                raise Exception
        except:
            flash('Liczba miesięcy musi być większa od 0', 'error')

        # Oprocentowanie stale
        if 'oprocentowanie_stale' in request.form:
            oprocentowanie_stale = request.form['oprocentowanie_stale']

            try:
                oprocentowanie_stale = float(okresy)
                if oprocentowanie_stale <= 0:
                    raise Exception
            except:
                flash('Oprocentowanie stałe musi być większe od 0', 'error')

        # marza
        marza = request.form['marza']

        try:
            marza = float(marza)
            if marza < 0:
                raise Exception
        except:
            flash('Marża musi być nie mniejsza niż 0', 'error')

        # prowizja
        prowizja = request.form['prowizja']

        try:
            prowizja = float(prowizja)
            if prowizja < 0:
                raise Exception
        except:
            flash('Prowizja musi być nie mniejsza niż 0', 'error')

        # pozaodsetkowe_koszty
        pozaodsetkowe_koszty = request.form['pozaodsetkowe_koszty']

        try:
            pozaodsetkowe_koszty = float(pozaodsetkowe_koszty)
            if pozaodsetkowe_koszty < 0:
                raise Exception
        except:
            flash('Pozaodsetkowe koszty kredytu muszą być nie mniejsze niż 0', 'error')


 

    return render_template('rrso/rrso.html')