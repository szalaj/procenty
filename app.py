
from flask import Flask, render_template, redirect, url_for, jsonify, request, make_response


import bank.kredyt as Kredyt

k1 = Kredyt.Kredyt('04/11/2021', '18/12/2021')

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


        I,D = Kredyt.rata_rowna_prosta(N, r, n, k=12)


        dane = {'kapital':N, 'zwrot':round(n*I,2), 'rata': I, 'liczba_rat': n, 'oprocentowanie': r}

        return render_template("main.html", dane=dane, dane_splaty=D)

    # tu zaczyna się aplikacja
    return render_template("main.html")


@app.route("/wibor", methods=['GET'])
def wibor():

    wibor_dane = [{'day': '04/11/2021', 'value': 0.21},
                  {'day': '04/02/2022', 'value': 3.05},
                  {'day': '04/05/2022', 'value': 6.30}]

    return render_template('wibor.html', wibor_dane = wibor_dane)


if __name__ == "__main__":
    print("welcome to bank app")
    app.run(debug=True)
