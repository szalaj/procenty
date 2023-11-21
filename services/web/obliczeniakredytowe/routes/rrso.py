

from flask import Blueprint, render_template, current_app, flash, redirect, url_for, request, send_file, sessions, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
import datetime as dt
import json
from obliczeniakredytowe import db
from dateutil.relativedelta import relativedelta

import utils.rrso as rs
import utils.proc as proc
from utils.generate_model import Wibor

rrso = Blueprint('rrso', __name__)



@rrso.route('/rrso', methods=['GET', 'POST'])
@login_required
def rrso_main():

    wynik_json = {}

    if request.method == 'POST':

        errors = False

        # data umowy
        data_umowy = request.form['data_umowy']

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
        
        try:
            if request.form['oprocentowanie_pozyczki'] == 'zmienne':
                wib = Wibor(request.form['rodzaj_wiboru'], db)
                max_wib = wib.max_wibor_date
                print(f"max wib {max_wib}")

                if data_umowy > max_wib:
                    raise Exception
                    
        except:
            errors = True
            flash(f"Dane dla WIBOR {request.form['rodzaj_wiboru']} dostępne do {max_wib.strftime('%d/%m/%Y')}", 'error')

        if not errors:

            wibor = None
            if 'oprocentowanie_stale' in request.form:
 
                stopa = oprocentowanie_stale + marza
            else:
                # pobierz wibor z bazy danych
                wibor = wib.getWibor(data_umowy)

                stopa = wibor + marza

            prowizja = udzielona_kwota - calkowita_kwota



            rata_calkowita_kwota = rs.rata_rowna(calkowita_kwota, okresy, stopa/100.0)
            rata_udzielona_kwota = rs.rata_rowna(udzielona_kwota, okresy, stopa/100.0)
            

            rrso = rs.RRSO(calkowita_kwota, [{'rata':rata_calkowita_kwota} for i in range(int(okresy))], stopa).oblicz_rrso()
            rrso_prowizja = rs.RRSO(calkowita_kwota, [{'rata':rata_udzielona_kwota} for i in range(int(okresy))], stopa).oblicz_rrso()
            

            # generuj raty
            dni_splaty = [(data_umowy + relativedelta(months=i+1)).strftime('%Y-%m-%d') for i in range(int(okresy))]

            dane_kredytu = {'start': data_umowy.strftime('%Y-%m-%d'), 'K':calkowita_kwota, 'p':stopa, 'marza':marza, 'daty_splaty':dni_splaty}
            kredyt = proc.create_kredyt(dane_kredytu, request.form['rodzaj_rat'])

            dane_kredytu_prowizja = {'start': data_umowy.strftime('%Y-%m-%d'), 'K':udzielona_kwota, 'p':stopa, 'marza':marza, 'daty_splaty':dni_splaty}
            kredyt_prowizja = proc.create_kredyt(dane_kredytu_prowizja, request.form['rodzaj_rat'])

            raty_porownanie = []
            for i,r in enumerate(kredyt['raty']):
                rr = {}
                rr['nr_raty'] = r['nr_raty']
                rr['dzien'] = r['dzien']
                rr['kapital'] = r['kapital']
                rr['odsetki'] = r['odsetki']
                rr['rata'] = r['rata']
                rr['kapital_prowizja'] = kredyt_prowizja['raty'][i]['kapital']
                rr['odsetki_prowizja'] = kredyt_prowizja['raty'][i]['odsetki']
                rr['rata_prowizja'] = kredyt_prowizja['raty'][i]['rata']

                rr['do_zwrotu_kapital'] = str(round(float(kredyt_prowizja['raty'][i]['kapital']) - float(r['kapital']),2))
                rr['do_zwrotu_odsetki'] = str(round(float(kredyt_prowizja['raty'][i]['odsetki']) - float(r['odsetki']),2))
                rr['do_zwrotu'] = str(round(float(kredyt_prowizja['raty'][i]['rata']) - float(r['rata']),2))
                raty_porownanie.append(rr)

            # pozaodsetkowe koszty
            #mpkk = calkowita_kwota*0.1 + calkowita_kwota*(okresy*30.41666/365)*0.1

            mpkk = rs.mpkk(calkowita_kwota, okresy, data_umowy)

            #print(f"mpkk: {mpkk}, mpkk2: {mpkk2}")

            wynik_json = {'rrso': round(rrso*100,4),
                          'rrso_prowizja': round(rrso_prowizja*100,4),
                          'stopa': round(stopa,4),
                          'wibor': wibor,
                          'prowizja': prowizja,
                          'mpkk': mpkk,
                          'raty_porownanie': raty_porownanie,                          
                          'raty': kredyt,
                          'raty_prowizja': kredyt_prowizja}

            # return dictionary wynik_json to html template as json


    return render_template('rrso/rrso.html', wynik_json=json.dumps(wynik_json))


