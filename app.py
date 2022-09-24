
from flask import Flask, render_template, redirect, url_for, jsonify, request, make_response
import datetime
from dateutil.relativedelta import relativedelta

import bank.kredyt
import bank.stopy
import bank.portfel
import bank.lokata

import json

app = Flask(__name__)

@app.route("/harmonogram", methods=['GET'])
def pokaz_harmonogram():
    '''
        Wybierz model kredytu
         - K
         - N
         - data uruchomienia
         - daty spłaty
         - rodzaj rata (stała/malejąca)
         - oprocentowanie
         - nadplaty
         - sposob rozliczania nadplat
         

         Wszystkie dane powinny być zapisane do modelu

         1. ModelKredyt
         2. Kredyt : Obliczenia danych kredytu podstawowych (ModelKredyt) 
         3. Opcjonalnie : Obliczenie Lokat (ModelLokata)
         4. Opcjonalnie, bbliczenia danych rzeczywistych

    '''
    K = 460000
    N = 360

    data_start = '04/11/2021'
  
    data_pierwszej_raty = datetime.datetime.strptime(data_start, "%d/%m/%Y")
    daty_splaty = [data_pierwszej_raty + relativedelta(months=i) for i in range(N)]

    inflacja = bank.stopy.getInflacja()
    nadplaty = bank.nadplaty.getNadplaty2()

    inflator = bank.portfel.Inflator(inflacja, '24/05/2022')
    stopy_procentowe = bank.stopy.getStopy(inflacja)
    wykres_stopy = bank.kredyt.Stopa(stopy_procentowe).getWykres(daty_splaty)

    kredyt_obj = bank.kredyt.StalaRata(K, N, data_start)
    kredyt_obj.setStopy(stopy_procentowe)
    kredyt_obj.setDatySplaty(daty_splaty)
    kredyt_obj.setNadplaty(nadplaty)

    res_kredyt1 = kredyt_obj.policz(inflator)

    inflacja_wykres_dane = [{'day': x['month'], 'value': x['rr'], 'value2': x['mm']} for x in inflacja]

    return render_template('harmonogram.html', wynik = res_kredyt1, wykres_stopy=wykres_stopy,inflacja_dane = inflacja_wykres_dane)








@app.route("/porownanie")
def porownanie():

    K = 460000
    N = 360


    inflacja = bank.stopy.getInflacja()
    nadplaty = bank.nadplaty.getNadplaty2()

    #stopy_procentowe = bank.stopy.wibor_moje
    stopy_procentowe = bank.stopy.getStopy(inflacja)



    data_start = '04/11/2021'
    data_koniec = '04/11/2051'

    data_pierwszej_raty = datetime.datetime.strptime('04/12/2021', "%d/%m/%Y")
    daty_splaty = [data_pierwszej_raty + relativedelta(months=i) for i in range(N)]




    inflator = bank.portfel.Inflator(inflacja, '24/05/2022')

    kredyt_obj = bank.kredyt.StalaRata(K,N, data_start)
    kredyt_obj.setStopy(stopy_procentowe)
    kredyt_obj.setDatySplaty(daty_splaty)

    res_kredyt1 = kredyt_obj.policz(inflator)


    kredyt_obj2 = bank.kredyt.StalaRata(K,N, data_start)
    kredyt_obj2.setStopy(stopy_procentowe)
    kredyt_obj2.setNadplaty(nadplaty)
    kredyt_obj2.setDatySplaty(daty_splaty)

    res_kredyt2 = kredyt_obj2.policz(inflator)


    portfel = bank.portfel.Portfel()
    portfel.dodajProdukt(kredyt_obj)
    #lok1 = bank.lokata.Lokata(1000,  '01/07/2022', data_koniec, 0.01)


    # data_pierwszej_lokaty = datetime.datetime.strptime('04/06/2028', "%d/%m/%Y")
    # for i in range(30):
    #     data_next = data_pierwszej_lokaty + relativedelta(months=i)
    #     lok = bank.lokata.Lokata(1000, data_next.strftime('%d/%m/%Y'), data_koniec, 0.06)
    #     portfel.dodajProdukt(lok)


    portfel2 = bank.portfel.Portfel()
    portfel2.dodajProdukt(kredyt_obj2)

    portfele_dane = []


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
    koszt_rozn = res_kredyt1[-1]['real_narastajaco_suma_kosztow']-res_kredyt2[-1]['real_narastajaco_suma_kosztow']
    print("portfelowa roznica : {}".format(port_rozn))
    print("kosztowa róznica : {}".format(koszt_rozn))
    print("roznica gdy lokata : {}".format(port_rozn-koszt_rozn))


    wykres_stopy = bank.kredyt.Stopa(stopy_procentowe).getWykres(daty_splaty)


    inflacja_wykres_dane = [{'day': x['month'], 'value': x['rr'], 'value2': x['mm']} for x in inflacja]



    return render_template('porownanie.html', results = res_kredyt1,
                                               results2 = res_kredyt2,
                                               wykres_stopy = wykres_stopy,
                                               inflacja_dane = inflacja_wykres_dane,
                                               portfele = portfele_dane)

@app.route("/portfel")
def portfel():
    return "portfel"


if __name__ == "__main__":
    print("welcome to bank app")
    app.run(debug=True)
