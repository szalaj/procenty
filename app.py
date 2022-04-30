
from flask import Flask, render_template, redirect, url_for, jsonify, request, make_response


import bank.kredyt as kredyt
import bank.stopy as stopy

k1 = kredyt.StalaRata(460000, 360, 4.23, '18/03/2022').policz()
print(k1)

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





if __name__ == "__main__":
    print("welcome to bank app")
    app.run(debug=True)
