

from flask import Blueprint, render_template, current_app, flash, redirect, url_for, request, send_file, sessions, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
import datetime as dt
import json
from obliczeniakredytowe import db

import utils.rrso as rs

rrso = Blueprint('rrso', __name__)



@rrso.route('/rrso', methods=['GET', 'POST'])
@login_required
def rrso_main():

    wynik_json = {}

    if request.method == 'POST':

        print(request.form)

        # data umowy
        data_umowy = request.form['data_umowy']
        errors = False

        try:
            data_umowy = dt.datetime.strptime(data_umowy, '%d/%m/%Y')
        except:
            errors = True
            flash('Niepoprawny format daty podpisania umowy. Poprawny format DD/MM/RRRR, np. 02/10/2021', 'error')

        # calkowita kwota kredytu
        calkowita_kwota = request.form['calkowita_kwota']

        try:
            calkowita_kwota = float(calkowita_kwota)
            if calkowita_kwota <= 0:
                raise Exception
        except:
            errors = True
            flash('Całkowita kwota kredytu musi być większa od 0', 'error')

        # Kwota udzielonego kredytu
        udzielona_kwota = request.form['udzielona_kwota']

        try:
            udzielona_kwota = float(udzielona_kwota)
            if udzielona_kwota <= 0:
                raise Exception
        except:
            errors = True
            flash('Kwota udzielonego kredytu musi być większa od 0', 'error')


        if not errors and udzielona_kwota < calkowita_kwota:
            errors = True
            flash('Kwota udzielonego kredytu nie może być mniejsza niż całkowita kwota kredytu. Wtedy prowizja < 0.', 'error')

        # Okresy
        okresy = request.form['okresy']

        try:
            okresy = float(okresy)
            if okresy <= 0:
                raise Exception
        except:
            errors = True
            flash('Liczba miesięcy musi być większa od 0', 'error')

        # Oprocentowanie stale
        if 'oprocentowanie_stale' in request.form:
            oprocentowanie_stale = request.form['oprocentowanie_stale']

            try:
                oprocentowanie_stale = float(oprocentowanie_stale)
                if oprocentowanie_stale <= 0:
                    raise Exception
            except:
                errors = True
                flash('Oprocentowanie stałe musi być większe od 0', 'error')

        # marza
        marza = request.form['marza']

        try:
            marza = float(marza)
            if marza < 0:
                raise Exception
        except:
            errors = True
            flash('Marża musi być nie mniejsza niż 0', 'error')


        # pozaodsetkowe_koszty
        pozaodsetkowe_koszty = request.form['pozaodsetkowe_koszty']

        try:
            pozaodsetkowe_koszty = float(pozaodsetkowe_koszty)
            if pozaodsetkowe_koszty < 0:
                raise Exception
        except:
            errors = True
            flash('Pozaodsetkowe koszty kredytu muszą być nie mniejsze niż 0', 'error')

        if not errors:


            if 'oprocentowanie_stale' in request.form:
 
                stopa = (oprocentowanie_stale + marza) / 100.0
            else:
                # pobierz wibor z bazy danych
                wibor = 2.11
                stopa = (wibor + marza) / 100.0

            print(f"stopa : {stopa}")
            rata = rs.rata_rowna(calkowita_kwota, okresy, stopa)
            print(rata)

            rrso = rs.RRSO(calkowita_kwota, [{'rata':rata} for i in range(int(okresy))],marza).oblicz_rrso()
            print(rrso)

            # create new variable and put stopa and rata into json variable

            wynik_json = {'rrso': rrso, 'stopa': stopa, 'rata': rata}

            # return dictionary wynik_json to html template as json


    return render_template('rrso/rrso.html', wynik_json=json.dumps(wynik_json))


