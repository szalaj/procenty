
from flask import Flask, render_template, redirect, url_for, jsonify, request, make_response
import datetime
from dateutil.relativedelta import relativedelta

import json
import yaml

app = Flask(__name__)


@app.route("/", methods=['GET'])
def main():

    with open("./results/last_result.yml", 'r') as yaml_in:
        yaml_object = yaml.safe_load(yaml_in)

    return render_template('wykres.html', dane=yaml_object)


if __name__ == "__main__":
    print("welcome proc")
    app.run(debug=True)
