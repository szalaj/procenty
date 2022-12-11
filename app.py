
from flask import Flask, render_template, redirect, url_for, jsonify, request, make_response
import datetime
from dateutil.relativedelta import relativedelta

import json
import yaml

import utils.generate_model

import utils.proc

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def main():

    if request.method == 'POST':

        opr = float(request.form['r_obnizki'])
        kapital = float(request.form['kapital'])

        utils.generate_model.generate('nowy_model2.yml', kapital, 2, 360, '2022-10-09', opr)
        kr = utils.proc.create_kredyt('nowy_model2')
        kr.symuluj()
        kr.zapisz_do_pliku('./results/last_result.yml')



    with open("./results/last_result.yml", 'r') as yaml_in:
        yaml_object = yaml.safe_load(yaml_in)

    return render_template('wykres.html', dane=yaml_object)



@app.route("/f", methods=['GET', 'POST'])
def formularz():

    return render_template('formularz.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
