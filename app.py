
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
    inflacja3 = bank.stopy.getInflacja3()

    nadplaty2 = [
                    {'nr': 0, 'day': '01/07/2023', 'value': 30000}]


    nadplaty = bank.nadplaty.getNadplaty2()

    wibor_moje = [
                    {'day': '04/11/2021', 'value': 4.23}]


    stopy_procentowe =bank.stopy.wibor_moje
    #stopy_procentowe =wibor_moje

    data_start = '04/11/2021'
    data_koniec = '04/11/2051'
    data_pierwszej_raty = datetime.datetime.strptime('04/12/2021', "%d/%m/%Y")
    daty_splaty = []

    for i in range(0, N):

        data_next = data_pierwszej_raty + relativedelta(months=i)

        # if i > 4:
        #     data_next = datetime.datetime.strptime('04/12/2021', "%d/%m/%Y") + relativedelta(months=i)

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

    inflator = bank.portfel.Inflator(inflacja, '24/05/2022')

    kredyt_obj = bank.kredyt.StalaRata(K,N, data_start)
    kredyt_obj.setStopy(stopy_procentowe)
    #kredyt_obj.setNadplaty(nadplaty)

    kredyt_obj.setDatySplaty(daty_splaty)
    #kredyt_obj.setRatyPobrane(raty_pobrane)

    res = kredyt_obj.policz(inflator)

    kredyt_obj2 = bank.kredyt.StalaRata(K,N, data_start)
    kredyt_obj2.setStopy(stopy_procentowe)



    kredyt_obj2.setNadplaty(nadplaty)

    kredyt_obj2.setDatySplaty(daty_splaty)
    #kredyt_obj2.setRatyPobrane(raty_pobrane)

    res2 = kredyt_obj2.policz(inflator)


    portfel = bank.portfel.Portfel()
    portfel.dodajProdukt(kredyt_obj)
    #lok1 = bank.lokata.Lokata(1000,  '01/07/2022', data_koniec, 0.01)
    data_pierwszej_lokaty = datetime.datetime.strptime('04/06/2028', "%d/%m/%Y")
    for i in range(30):
        data_next = data_pierwszej_lokaty + relativedelta(months=i)
        lok = bank.lokata.Lokata(1000, data_next.strftime('%d/%m/%Y'), data_koniec, 0.06)
        portfel.dodajProdukt(lok)


    #portfel.dodajProdukt(lok1)



    portfel2 = bank.portfel.Portfel()
    portfel2.dodajProdukt(kredyt_obj2)
    #portfel2.dodajProdukt(lok1)
    #portfel2.dodajProdukt(lok2)


    portfele_dane = []


    #startd = datetime.datetime.strptime('18/12/2021', "%d/%m/%Y")

    data_start_dt =  datetime.datetime.strptime(data_start, "%d/%m/%Y")
    data_koniec_dt = datetime.datetime.strptime(data_koniec, "%d/%m/%Y")



    liczba_miesiecy = (data_koniec_dt.year - data_start_dt.year) * 12 + data_koniec_dt.month - data_start_dt.month

    for i in range(1,liczba_miesiecy-1):

        data_next = data_pierwszej_raty + relativedelta(months=i)
        month = data_next.strftime('%m/%Y')
        saldo_norm = portfel.getSumaSald(month)
        saldo_norm2 = portfel2.getSumaSald(month)

        saldo_real = inflator.oblicz(saldo_norm, data_next)
        saldo_real2 = inflator.oblicz(saldo_norm2, data_next)
        #.strftime('%d/%m/%Y')

        portfele_dane.append({'month': month,
                             'p1_saldo_norm': saldo_norm,
                             'p1_saldo_real': saldo_real,
                             'p2_saldo_norm': saldo_norm2,
                             'p2_saldo_real': saldo_real2 })


    port_rozn = portfele_dane[-1]['p1_saldo_real']-portfele_dane[-1]['p2_saldo_real']
    koszt_rozn = res[-1]['real_narastajaco_suma_kosztow']-res2[-1]['real_narastajaco_suma_kosztow']
    print("portfelowa roznica : {}".format(port_rozn))
    print("kosztowa róznica : {}".format(koszt_rozn))
    print("roznica gdy lokata : {}".format(port_rozn-koszt_rozn))

    suma_kosztow = kredyt_obj.getSumaKosztow()
    wykres_stopy = bank.kredyt.Stopa(stopy_procentowe).getWykres(daty_splaty)

    inflacja_wykres_dane = [{'day': key, 'value': value} for key, value in inflacja.items()]


    inflacja_wykres_dane = [{'day': x['month'], 'value': x['rr']} for x in inflacja3]



    return render_template('harmonogram.html', results = res,
                                               results2 = res2,
                                               wykres_stopy = wykres_stopy,
                                               suma_kosztow = suma_kosztow,
                                               inflacja_dane = inflacja_wykres_dane,
                                               portfele = portfele_dane)


@app.route("/portfel")
def portfel():
    return "portfel"


if __name__ == "__main__":
    print("welcome to bank app")
    app.run(debug=True)
