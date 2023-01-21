
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
            kapital1 = float(request.form['kapital1'])
            dataStart1 = str(request.form['dataStart1'])
            okresy = int(request.form['okresy'])
            marza = float(request.form['marza'])

            rodzajWiboru = str(request.form['rodzajWiboru'])
            rodzajRat = str(request.form['rodzajRat'])
            dataZamrozenia = str(request.form['dataZamrozenia'])


            data_start1 = dt.datetime.strptime(dataStart1, '%d/%m/%Y')
            data_zamrozenia = dt.datetime.strptime(dataZamrozenia, '%d/%m/%Y')

            print(request.form)

            checkTr2 = False
            checkTr3 = False

            if 'checkTransza2' in request.form:
                checkTr2 = True
                kapital2 = float(request.form['kapital2'])
                dataStart2 = str(request.form['dataStart2'])
                data_start2 = dt.datetime.strptime(dataStart2, '%d/%m/%Y')


            if 'checkTransza3' in request.form:
                checkTr3 = True
                kapital3 = float(request.form['kapital3'])
                dataStart3 = str(request.form['dataStart3'])
                data_start3 = dt.datetime.strptime(dataStart3, '%d/%m/%Y')


        except:
            error = "Wypełnij poprawnie formularz"
            flash('m')
            return render_template('wykres.html')

        

        print(rodzajWiboru)



        #dane_kredytu = utils.generate_model.generate(kapital, 2, 360, start_date, opr)

        dane_kredytu =  utils.generate_model.generateFromWiborFile(kapital1, okresy, data_start1, marza, 0)
        dane_kredytu_alt =  utils.generate_model.generateFromWiborFile(kapital1, okresy, data_start1, marza, 0)

        wynik = utils.proc.create_kredyt(dane_kredytu)
        wynik2 = utils.proc.create_kredyt(dane_kredytu_alt)


        form_data = {"kapital":kapital1,
                     "datestart":dataStart1,
                     "okresy":okresy,
                     "marza":marza}
                                                                                    




        return render_template('wykres.html', dane=wynik, dane2=wynik2, form_data=form_data)



    return render_template('wykres.html')






if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
