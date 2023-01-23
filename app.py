
from flask import Flask, render_template, flash, redirect, url_for, jsonify, request, make_response
import datetime as dt
import utils.generate_model
import utils.proc


from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from http import HTTPStatus

app = Flask(__name__)
app.secret_key = '33a42d649ff6cfd8662d550dabc5c3dbed65e34223c41ef2f24362133d829042'

login_manager = LoginManager()
login_manager.init_app(app)

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

@app.route("/", methods=['GET', 'POST'])
@login_required
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

        

        dane_kredytu =  utils.generate_model.generateFromWiborFile(kapital1, okresy, data_start1, marza, data_zamrozenia, rodzajWiboru, transze, False)

        dane_kredytu_alt =  utils.generate_model.generateFromWiborFile(kapital1, okresy, data_start1, marza, data_zamrozenia, rodzajWiboru, transze, True)

        wynik = utils.proc.create_kredyt(dane_kredytu, rodzajRat)
        wynik2 = utils.proc.create_kredyt(dane_kredytu_alt, rodzajRat)


        form_data = {"kapital1":kapital1,
                     "dataStart1":dataStart1,
                     "okresy":okresy,
                     "marza":marza,
                     "dataZamrozenia":dataZamrozenia,
                     "rodzajWiboru":rodzajWiboru,
                     "rodzajRat":rodzajRat}

        form_data['checkTr2'] = checkTr2
        form_data['checkTr3'] = checkTr3

        if checkTr2:
            form_data['kapital2'] = kapital2
            form_data['dataStart2'] = dataStart2

        if checkTr3:
            form_data['kapital3'] = kapital3
            form_data['dataStart3'] = dataStart3


        return render_template('wykres.html', dane=wynik, dane2=wynik2, data_zamrozenia=data_zamrozenia.strftime('%Y-%m-%d'), form_data=form_data)



    return render_template('wykres.html')






if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
