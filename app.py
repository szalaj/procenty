
from flask import Flask, render_template, flash, redirect, url_for, jsonify, request, make_response
import datetime
from dateutil.relativedelta import relativedelta

import json
import yaml

import datetime as dt

import utils.generate_model

import utils.proc

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/", methods=['GET', 'POST'])
def main():

    if request.method == 'POST':

        error = None

        try:
            kapital = float(request.form['kapital'])
            datestart = str(request.form['datastart'])
            okresy = int(request.form['okresy'])

            if not (request.form['r_obnizki']).isdigit():
                obnizacz = 0
            else:
                obnizacz = float(request.form['r_obnizki'])

            start_date = dt.datetime.strptime(datestart, '%d/%m/%Y')
        except:
            error = "Wypełnij poprawnie formularz"
            flash('You were successfully logged in')
            return render_template('wykres.html')

        

        #dane_kredytu = utils.generate_model.generate(kapital, 2, 360, start_date, opr)

        dane_kredytu =  utils.generate_model.generateFromWiborFile(kapital, okresy, start_date, 2.99, 0)
        dane_kredytu_alt =  utils.generate_model.generateFromWiborFile(kapital, okresy, start_date, 2.99, obnizacz)

        kr = utils.proc.create_kredyt(dane_kredytu)
        wynik = kr.symuluj()

        kr2 = utils.proc.create_kredyt(dane_kredytu_alt)
        wynik2 = kr2.symuluj()

        form_data = {"kapital":kapital,
                     "datestart":datestart,
                     "okresy":okresy,
                     "obnizacz":obnizacz}
                                                                                    




        return render_template('wykres.html', dane=wynik, dane2=wynik2, form_data=form_data)



    return render_template('wykres.html')






if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
