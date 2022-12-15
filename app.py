
from flask import Flask, render_template, redirect, url_for, jsonify, request, make_response
import datetime
from dateutil.relativedelta import relativedelta

import json
import yaml

import datetime as dt

import utils.generate_model

import utils.proc

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def main():

    if request.method == 'POST':

        
        kapital = float(request.form['kapital'])
        datestart = str(request.form['datastart'])
        okresy = int(request.form['okresy'])
        opr = float(request.form['r_obnizki'])

        start_date = dt.datetime.strptime(datestart, '%d/%m/%Y')

        #dane_kredytu = utils.generate_model.generate(kapital, 2, 360, start_date, opr)

        dane_kredytu =  utils.generate_model.generateFromWiborFile(kapital, okresy, start_date)

        kr = utils.proc.create_kredyt(dane_kredytu)
        wynik = kr.symuluj()


       


        return render_template('wykres.html', dane=wynik)



    return render_template('wykres.html', dane={})



@app.route("/f", methods=['GET', 'POST'])
def formularz():

    return render_template('formularz.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
