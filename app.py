
from flask import Flask, render_template, flash, redirect, url_for, jsonify, request, make_response
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

            transze = []

            if 'checkTransza2' in request.form:
                checkTr2 = True
                kapital2 = float(request.form['kapital2'])
                dataStart2 = str(request.form['dataStart2'])
                data_start2 = dt.datetime.strptime(dataStart2, '%d/%m/%Y')

                transze.append({'dzien': data_start2, 'wartosc':kapital2 })

            if 'checkTransza3' in request.form:
                checkTr3 = True
                kapital3 = float(request.form['kapital3'])
                dataStart3 = str(request.form['dataStart3'])
                data_start3 = dt.datetime.strptime(dataStart3, '%d/%m/%Y')

                transze.append({'dzien': data_start3, 'wartosc':kapital3 })

        except:
            error = "Wypełnij poprawnie formularz"
            flash('m')
            return render_template('wykres.html')

        

        dane_kredytu =  utils.generate_model.generateFromWiborFile(kapital1, okresy, data_start1, marza, data_zamrozenia, transze)

        dane_kredytu_alt =  utils.generate_model.generateFromWiborFile(kapital1, okresy, data_start1, marza, data_zamrozenia, transze)

        wynik = utils.proc.create_kredyt(dane_kredytu)
        wynik2 = utils.proc.create_kredyt(dane_kredytu_alt)




        form_data = {"kapital1":kapital1,
                     "dataStart1":dataStart1,
                     "okresy":okresy,
                     "marza":marza,
                     "dataZamrozenia":dataZamrozenia}

        form_data['checkTr2'] = checkTr2
        form_data['checkTr3'] = checkTr3

        if checkTr2:
            form_data['kapital2'] = kapital2
            form_data['dataStart2'] = dataStart2

        if checkTr3:
            form_data['kapital3'] = kapital3
            form_data['dataStart3'] = dataStart3


        return render_template('wykres.html', dane=wynik, dane2=wynik2, form_data=form_data)



    return render_template('wykres.html')






if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
