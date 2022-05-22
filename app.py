
from flask import Flask, render_template, redirect, url_for, jsonify, request, make_response
import datetime
from dateutil.relativedelta import relativedelta

import bank.kredyt
import bank.stopy
import bank.portfel
import bank.lokata



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

    inflacja = bank.stopy.getInflacja2()

    data_pierwszej_raty = datetime.datetime.strptime('18/12/2021', "%d/%m/%Y")
    daty_splaty = []

    for i in range(0, N):

        data_next = data_pierwszej_raty + relativedelta(months=i)

        if i > 4:
            data_next = datetime.datetime.strptime('04/12/2021', "%d/%m/%Y") + relativedelta(months=i)

        daty_splaty.append(data_next)

    raty_pobrane =   [{'nr': 1, 'kwota': 2261.13},
                      {'nr': 2, 'kwota': 1737.09+524.04},
                      {'nr': 3, 'kwota': 2147.70+113.43},
                      {'nr': 4, 'kwota': 2484.34+594.04},
                      {'nr': 5, 'kwota': 2746.95+331.43},
                      {'nr': 6, 'kwota': 1411.47+1637.38},
                      {'nr': 7, 'kwota':  4000.55}
                       ]

    #raty_pobrane = []

    kredyt_obj = bank.kredyt.StalaRata(K,N, '04/11/2021')
    kredyt_obj.setStopy(bank.stopy.wibor_moje)
    kredyt_obj.setNadplaty(bank.nadplaty.getNadplaty())

    kredyt_obj.setDatySplaty(daty_splaty)
    kredyt_obj.setRatyPobrane(raty_pobrane)

    res = kredyt_obj.policz()

    kredyt_obj2 = bank.kredyt.StalaRata(K,N, '04/11/2021')
    kredyt_obj2.setStopy(bank.stopy.wibor_moje)
    kredyt_obj2.setNadplaty(bank.nadplaty.getNadplaty2())

    kredyt_obj2.setDatySplaty(daty_splaty)
    kredyt_obj2.setRatyPobrane(raty_pobrane)

    res2 = kredyt_obj2.policz()



    lok1 = bank.lokata.Lokata(1000, '01/07/2022', '01/07/2055', 0.04)
    lok2 = bank.lokata.Lokata(50000, '01/07/2023', '01/07/2055', 0.1)

    portfel = bank.portfel.Portfel()
    portfel.dodajProdukt(kredyt_obj)
    portfel.dodajProdukt(lok1)
    portfel.dodajProdukt(lok2)


    portfel_dane = []
    inflator = bank.portfel.Inflator(inflacja)

    #startd = datetime.datetime.strptime('18/12/2021', "%d/%m/%Y")

    for i in range(1,380):

        data_next = data_pierwszej_raty + relativedelta(months=i)
        month = data_next.strftime('%m/%Y')
        saldo_norm = portfel.getSumaSald(month)

        saldo_real = inflator.oblicz(saldo_norm, '01/05/2022', data_next.strftime('%d/%m/%Y'))

        portfel_dane.append({'month': month,
                             'value': saldo_norm,
                             'value2': saldo_real })





    suma_kosztow = kredyt_obj.getSumaKosztow()
    wykres_stopy = bank.kredyt.Stopa(bank.stopy.wibor_moje).getWykres(daty_splaty)

    inflacja_wykres_dane = [{'day': key, 'value': value} for key, value in inflacja.items()]



    return render_template('harmonogram.html', results = res,
                                               results2 = res2,
                                               wykres_stopy = wykres_stopy,
                                               suma_kosztow = suma_kosztow,
                                               inflacja_dane = inflacja_wykres_dane,
                                               portfel = portfel_dane)


@app.route("/portfel")
def portfel():
    return "portfel"


if __name__ == "__main__":
    print("welcome to bank app")
    app.run(debug=True)
