
from flask import Flask, render_template, redirect, url_for, jsonify, request, make_response
import datetime
from dateutil.relativedelta import relativedelta

import bank.kredyt
import bank.stopy



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

    wibor_dane = bank.stopy.wibor_moje

    kr = bank.kredyt.Kredyt(460000, '04/11/2021', '18/12/2021')

    yo = kr.policz_kredyt()

    roznice_opcje = kr.oblicz_roznice()

    return render_template('stopy.html', wibor_dane = wibor_dane, roznice_opcje = roznice_opcje)



@app.route("/harmonogram", methods=['GET'])
def pokaz_harmonogram():

    K = 460000
    N = 360

    inflacja = bank.stopy.getInflacja()
    data_pierwszej_raty = datetime.datetime.strptime('18/12/2021', "%d/%m/%Y")
    daty_splaty = []

    for i in range(0, N):

        data_next = data_pierwszej_raty + relativedelta(months=i)

        if i > 4:
            data_next = datetime.datetime.strptime('04/12/2021', "%d/%m/%Y") + relativedelta(months=i)

        daty_splaty.append(data_next)

    raty_pobrane = [{'nr': 1, 'kwota': 2261.13},
                      {'nr': 2, 'kwota': 1737.09+524.04},
                      {'nr': 3, 'kwota': 2147.70+113.43},
                      {'nr': 4, 'kwota': 2484.34+594.04},
                      {'nr': 5, 'kwota': 2746.95+331.43},
                      {'nr': 6, 'kwota': 1411.47+1637.38},
                      {'nr': 7, 'kwota':  4000.55}
                  ]

    kredyt_obj = bank.kredyt.StalaRata(K,N, '04/11/2021')
    kredyt_obj.setStopy(bank.stopy.wibor_moje)
    kredyt_obj.setNadplaty(bank.nadplaty.getNadplaty())
    kredyt_obj.setInflacja(inflacja)

    kredyt_obj.setDatySplaty(daty_splaty)

    kredyt_obj.setRatyPobrane(raty_pobrane)

    res = kredyt_obj.policz()

    suma_kosztow = kredyt_obj.getSumaKosztow()
    real_suma = kredyt_obj.getRealnaSumaKosztow()

    wykres_stopy = bank.kredyt.Stopa(bank.stopy.wibor_moje).getWykres(daty_splaty)




    return render_template('harmonogram.html', results = res,
                                               wykres_stopy = wykres_stopy,
                                               suma_kosztow = suma_kosztow,
                                               real_suma = real_suma,
                                               inflacja_dane = inflacja)



if __name__ == "__main__":
    print("welcome to bank app")
    app.run(debug=True)
