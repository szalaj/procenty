
from flask import Flask, render_template, flash, redirect, url_for, jsonify, request, make_response, send_file


from wtforms import Form, BooleanField, StringField, PasswordField, SelectField, validators

import datetime as dt
import utils.generate_model
import utils.proc


from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from http import HTTPStatus

import pandas as pd

from docx import Document
from io import BytesIO

import requests

app = Flask(__name__)
app.secret_key = '33a42d649ff6cfd8662d550dabc5c3dbed65e34223c41ef2f24362133d829042'


login_manager = LoginManager()
login_manager.init_app(app)


class KredytForm(Form):

    kapital1 = StringField('Kapitał - Transza 1.', [validators.Length(min=1, max=25)], description="Ile?")
    kapital2 = StringField('Kapitał - Transza 2.', [validators.Length(min=1, max=25)], description="Ile?")
    kapital3 = StringField('Kapital - Transza 3.', [validators.Length(min=1, max=25)], description="Ile?")
    dataStart1 = StringField('Data uruchomienia 1', [validators.Length(min=1, max=25)], description="DD/MM/YYYY")
    dataStart2 = StringField('Data uruchomienia 2', [validators.Length(min=1, max=25)], description="DD/MM/YYYY")
    dataStart3 = StringField('Data uruchomienia 3', [validators.Length(min=1, max=25)], description="DD/MM/YYYY")
    okresy = StringField('Ilość miesięcy', [validators.Length(min=1, max=25)], description="a")
    marza = StringField('Marża', [validators.Length(min=1, max=25)], description="%")
    dataZamrozenia = StringField('Data zamrozenia', [validators.Length(min=1, max=25)], description="DD/MM/YYYY")
    rodzajWiboru = SelectField('Rodzaj wiboru', choices=[('3M', '3M'), ('6M', '6M')])
    rodzajRat = SelectField('Rodzaj rat', choices=[('stale', 'stałe'), ('malejace', 'malejące')])




class User(UserMixin):   
    id = 1
    name = 'aa'
    password = 'a'
    email = 'a@b'                                                                                               
    def to_json(self):        
        return {"name": self.name,
                "email": self.email}

    def is_authenticated(self):
        return True

    def is_active(self):   
        return True           

    def is_anonymous(self):
        return False          

    def get_id(self):         
        return str(User.id)

@login_manager.user_loader
def load_user(user_id):
    return User()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    if request.method == 'POST':

        
        uzytkownik = str(request.form['uzytkownik'])
        haslo = str(request.form['haslo'])
        if uzytkownik == 'kancelaria' and haslo =='wps':    
        
            login_user(User())
            return redirect(url_for('main'))

    return render_template('login.html')

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

@app.route("/formularz", methods=['GET', 'POST'])
@login_required
def formularz():

    form = KredytForm(request.form)
    print(form.validate())
    message = ""
    if request.method == 'POST' and form.validate():
        print('validate')
        name = form.name.data
        flash('Thanks for registering')
        return redirect(url_for('main'))
       
    

    return render_template('formularz.html', form=form, message=message)
    


@app.route("/", methods=['GET', 'POST'])
@login_required
def main():

    df3 = pd.read_csv('static/plopln3m_d.csv', usecols=[0,1], index_col=0)
    df3.index = pd.to_datetime(df3.index, format='%Y-%m-%d')

    df6 = pd.read_csv('static/plopln6m_d.csv', usecols=[0,1], index_col=0)
    df6.index = pd.to_datetime(df6.index, format='%Y-%m-%d')

    max_day_wibor3m = df3.index.max()
    max_day_wibor6m = df6.index.max()

    tech_data = {'max_day_wibor3m': max_day_wibor3m.strftime('%d-%m-%Y'),
               'max_day_wibor6m': max_day_wibor6m.strftime('%d-%m-%Y')}

    

    if request.method == 'POST':

        error = None

        form_data = {"kapital1":request.form['kapital1'],
                     "kapital2":request.form['kapital2'],
                     "kapital3":request.form['kapital3'],
                     "dataStart1":request.form['dataStart1'],
                     "dataStart2":request.form['dataStart2'],
                     "dataStart3":request.form['dataStart3'],
                     "okresy":request.form['okresy'],
                     "marza":request.form['marza'],
                     "dataZamrozenia":request.form['dataZamrozenia'],
                     "rodzajWiboru":request.form['rodzajWiboru'],
                     "rodzajRat":request.form['rodzajRat']}

        if 'checkTransza2' in request.form:
            form_data['checkTr2'] = True


        if 'checkTransza3' in request.form:
            form_data['checkTr3'] = True

        tech_data['form_data'] = form_data

        try:
            kapital1 = float(form_data['kapital1'])
            dataStart1 = str(form_data['dataStart1'])
            okresy = int(form_data['okresy'])
            marza = float(form_data['marza'])

            rodzajWiboru = str(form_data['rodzajWiboru'])
            rodzajRat = str(form_data['rodzajRat'])
            dataZamrozenia = str(form_data['dataZamrozenia'])


            data_start1 = dt.datetime.strptime(dataStart1, '%d/%m/%Y')
            data_zamrozenia = dt.datetime.strptime(dataZamrozenia, '%d/%m/%Y')

            transze = []

            if 'checkTransza2' in request.form:
                kapital2 = float(form_data['kapital2'])
                dataStart2 = str(form_data['dataStart2'])
                data_start2 = dt.datetime.strptime(dataStart2, '%d/%m/%Y')

                transze.append({'dzien': data_start2, 'wartosc':kapital2 })

            if 'checkTransza3' in request.form:
                kapital3 = float(form_data['kapital3'])
                dataStart3 = str(form_data['dataStart3'])
                data_start3 = dt.datetime.strptime(dataStart3, '%d/%m/%Y')

                transze.append({'dzien': data_start3, 'wartosc':kapital3 })


            

            if data_zamrozenia > max_day_wibor3m if rodzajWiboru=='3M' else data_zamrozenia > max_day_wibor6m:
                error = "Data zamrożenia wiboru większa niż dostępne dane."
                flash('m')
                return render_template('wykres.html', error=error, tech_data=tech_data)




        except:
            error = "Wypełnij poprawnie formularz"
            flash('m')
            return render_template('wykres.html', error=error, tech_data=tech_data)

        

        dane_kredytu =  utils.generate_model.generateFromWiborFile(kapital1, okresy, data_start1, marza, data_zamrozenia, rodzajWiboru, transze, False)

        wibor_start = dane_kredytu["p"]
        zamrozona_stopa = round(dane_kredytu["p"] + marza,2)
     
        dane_kredytu_alt =  utils.generate_model.generateFromWiborFile(kapital1, okresy, data_start1, zamrozona_stopa, data_zamrozenia, rodzajWiboru, transze, True)


        wynik = utils.proc.create_kredyt(dane_kredytu, rodzajRat)
        wynik2 = utils.proc.create_kredyt(dane_kredytu_alt, rodzajRat)

        fin_data = {}
        fin_data['dane'] = wynik
        fin_data['dane2'] = wynik2

        fin_data['data_zamrozenia'] = data_zamrozenia
        fin_data['wibor_start'] = wibor_start

        
        fin_data['zamrozona_stopa'] = zamrozona_stopa

        
        return render_template('wykres.html', tech_data=tech_data, fin_data=fin_data)



    return render_template('wykres.html', tech_data=tech_data)


@app.route("/doc", methods=['GET', 'POST'])
@login_required
def get_doc():

    document = Document()
    document.add_heading("Sample Press Release", 0)
    f = BytesIO()
    # do staff with document
    document.save(f)
    f.seek(0)

    return send_file(
        f,
        as_attachment=True,
        download_name   ='report.docx'
    )

@app.route("/wibor", methods=['GET', 'POST'])
@login_required
def wibor():

    response6m = requests.get('https://stooq.pl/q/d/l/?s=plopln6m&i=d')
    
    with open("./static/plopln6m_d.csv", "wb") as f:
        f.write(response6m.content)

    response3m = requests.get('https://stooq.pl/q/d/l/?s=plopln3m&i=d')
    
    with open("./static/plopln3m_d.csv", "wb") as f:
        f.write(response3m.content)
    
    return redirect(url_for('main'))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
    #app.run(host='0.0.0.0', port=5000, debug=True)
