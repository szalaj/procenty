
from flask import Flask, render_template, redirect, url_for, jsonify, request, make_response


import bank.kredyt as kredyt
import bank.stopy as stopy



app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def main():



    # tu po wypełnieniu i przesłaniu formularza
    if request.method == "POST":

        req = request.form


        # missing
        missing = list()

        for k, v in req.items():

            if v=="":
                missing.append(k)

        if missing:
            feedback = f"Brak danych dla {', '.join(missing)}"
            return render_template("main.html", feedback=feedback)


        # zmienne
        # pozyczony kapital
        N = float(req["kapital"])

        # oprocentowanie
        r = float(req["procent"])/100

        # liczba rat
        n = int(req["liczba_rat"])


        print("--obliczenia--")


        I,D = kredyt.rata_rowna_prosta(N, r, n, k=12)


        dane = {'kapital':N, 'zwrot':round(n*I,2), 'rata': I, 'liczba_rat': n, 'oprocentowanie': r}

        return render_template("main.html", dane=dane, dane_splaty=D)

    # tu zaczyna się aplikacja
    return render_template("main.html")


@app.route("/stopy", methods=['GET'])
def pokaz_stopy():

    wibor_dane = stopy.wibor_moje

    kr = kredyt.Kredyt(460000, '04/11/2021', '18/12/2021')

    yo = kr.policz_kredyt()

    roznice_opcje = kr.oblicz_roznice()

    return render_template('stopy.html', wibor_dane = wibor_dane, roznice_opcje = roznice_opcje)

@app.route("/harmonogram", methods=['GET'])
def pokaz_harmonogram():

    #k, res = kredyt.StalaRata(430000, 350, 4.23, '01/11/2021').policz()

    res, raty_suma, real_suma, wykres_stopy = kredyt.StalaRata(460000, 360, 4.23, '04/11/2021').policz('18/12/2021')

    kt = 100*pow(1-0.1, 30)
    print('wartosc ', kt)
    A = 100
    for i in range(0,30):
        A = A - 0.1*A

    print(A)


    return render_template('harmonogram.html', results = res, raty_suma = raty_suma, real_suma = real_suma, wykres_stopy=wykres_stopy)



if __name__ == "__main__":
    print("welcome to bank app")
    app.run(debug=True)
