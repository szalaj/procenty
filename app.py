
from flask import Flask, render_template, redirect, url_for, jsonify, request, make_response
import datetime
from dateutil.relativedelta import relativedelta

import json
import yaml

import generate_model
import proc

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def main():

    if request.method == 'POST':

        opr = float(request.form['opr_max'])

        generate_model.generate('nowy_model2.yml', 8888, 2, 120, '2022-10-09', opr)
        kr = proc.create_kredyt('nowy_model2')
        kr.symuluj()
        kr.zapisz_do_pliku('./results/last_result.yml')

    else:
        pass

    with open("./results/last_result.yml", 'r') as yaml_in:
        yaml_object = yaml.safe_load(yaml_in)

    return render_template('wykres.html', dane=yaml_object)


if __name__ == "__main__":
    print("welcome proc")
    app.run(debug=True)
