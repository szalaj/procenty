


import datetime
from dateutil.relativedelta import relativedelta

import bank.stopy
import bank.nadplaty

import pandas as pd

def rata_rowna_prosta(K0, r, N, k):

    # K - Kapitał
    # r - oprocentowanie r% / 100
    # N - liczba okresow
    # k - liczba platnosci rat w roku (12)

    L = (K0*r)
    M = k*(1-pow(k/(k+r),N) )

    I = L/M

    #I = round(I, 2)

    K = K0
    Dane = []
    for okres in range(N):



        odsetki = r/12 * K

        k_splata = I - odsetki



        K = K - k_splata

        Dane.append({
            'okres':okres,
            'kapital_p':K+k_splata,
            'kapital_k':K,
            'odsetki':odsetki,
            'k_splata':k_splata,
            'rata':odsetki+k_splata
        })


    print("kapital na koncu {}".format(K))



    return I,Dane


def rata_rowna(N0, r, n, k):
    """
    Parameters
    ----------
    N0 - pozyczona kwota do splaty
    r - stopa procentowa roczna
    n - ilosc okresow splaty (miesiecy)
    k - ile rat w roku placonych
    """
    L = (N0*r)
    M = k*(1-pow(k/(k+r),n) )

    I = L/M
    return I



class Stopa:
    """
    Obiekty do łatwiejszego wyliczania obowiązującej stopy procentowej w danym dniu

    Parameters:
    -----------------------
    stopa_dane_json - patrz format w bank.stopy
    """

    def __init__(self, stopa_dane_json):


        self.stopa_df = pd.DataFrame(stopa_dane_json)
        self.stopa_df['day'] = pd.to_datetime(self.stopa_df['day'], format="%d/%m/%Y")
        self.stopa_df = self.stopa_df.sort_values(by="day")


    def getStopa(self, day):

        r_day = self.stopa_df[self.stopa_df['day']<=day]['value'].iloc[-1] / 100.0

        return r_day

    def pomiedzy(self, data1, data2):

        zwrot = self.stopa_df[(self.stopa_df['day']>data1) & (self.stopa_df['day']<data2)]

        if not zwrot.empty:

            zwrot_list = []

            for i, row in zwrot.iterrows():

                zwrot_list.append({'dzien': row['day'], 'stopa': row['value']/100.0})


            return zwrot_list

        else:

            return None

class Nadplata:
    """
    Obiekty do łatwiejszego wyliczania obowiązującej stopy procentowej w danym dniu

    Parameters:
    -----------------------
    stopa_dane_json - patrz format w bank.stopy
    """

    def __init__(self, nadplata_dane_json):


        self.nadplata_df = pd.DataFrame(nadplata_dane_json)
        self.nadplata_df['day'] = pd.to_datetime(self.nadplata_df['day'], format="%d/%m/%Y")
        self.nadplata_df = self.nadplata_df.sort_values(by="day")


    def show(self):
        pass
        #print(self.nadplata_df)


    def pomiedzy(self, data1, data2):

        zwrot = self.nadplata_df[(self.nadplata_df['day']>=data1) & (self.nadplata_df['day']<data2)]

        if not zwrot.empty:

            zwrot_list = []

            for i, row in zwrot.iterrows():

                zwrot_list.append({'nr': row['nr'], 'dzien': row['day'], 'wartosc': row['value']})


            return zwrot_list

        else:

            return None



class Zdarzenie:

    def __init__(self, data, r, saldo):

        self.data = data
        self.r = r
        self.saldo = saldo

    def __eq__(self, data_other):
        return self.data == data_other

    def __lt__(self, other):
         return self.data < other.data



    def __repr__(self):
        return 'Zdarzenie {}, {}, {}'.format(self.data.strftime('%d/%m/%Y'), self.r, self.saldo)






class KrokSplaty:

    def __init__(self, nr):

        self.krok_nr = nr
        self.data_splaty = ''
        self.saldo_start = 0
        self.saldo_koniec = 0
        self.rata = 0
        self.nadplaty = 0
        self.splata_kapitalu = 0
        self.odsetki_krok = 0
        self.odsetki_narastajaco = 0
        self.inne_oplaty = 0
        self.suma_kosztow = 0
        self.realna_suma_kosztow = 0




class StalaRata:


    def __init__(self, K0, N, dzien_start):



        self.K0 = K0
        self.N = N
        #self.dzien_uruchomienia =
        self.dzien_start = datetime.datetime.strptime(dzien_start, "%d/%m/%Y")




    def nalicz_odsetki(self, Kapital,  r_roczne, dzien_start, dzien_koniec):

        dni_odsetkowe = (dzien_koniec-dzien_start).days
        stopa_dzien = r_roczne / 365.0
        odsetki = Kapital * stopa_dzien * dni_odsetkowe

        return odsetki








    def policz(self, data_rata):

        raty_pobrane = [{'nr': 1, 'kwota': 2261.13},
                          {'nr': 2, 'kwota': 1737.09+524.04},
                          {'nr': 3, 'kwota': 2147.70+113.43},
                          {'nr': 4, 'kwota': 2484.34+594.04},
                          {'nr': 5, 'kwota': 2746.95+331.43},
                          {'nr': 6, 'kwota': 1411.47+1637.38},
                          {'nr': 7, 'kwota':  4000.65}
                      ]

        data_pierwszej_raty = datetime.datetime.strptime(data_rata, "%d/%m/%Y")


        daty_splaty = []
        for i in range(0, self.N):

            data_next = data_pierwszej_raty + relativedelta(months=i)

            if i > 4:
                data_next = datetime.datetime.strptime('04/12/2021', "%d/%m/%Y") + relativedelta(months=i)

            daty_splaty.append(data_next)







        result =  [{'nr': 0,
                'data': self.dzien_start.strftime('%d/%m/%Y'),
                'saldo_start':"{:,.2f} zł".format(self.K0),
                'saldo_koniec':"{:,.2f} zł".format(self.K0),
                'rata':   "{:,.2f} zł".format(0),
                'nadplaty':   "{:,.2f} zł".format(0),
                'kapital_splata': "{:,.2f} zł".format(0),
                'odsetki': "{:,.2f} zł".format(0),
                'inne_oplaty': "{:,.2f} zł".format(0),
                'suma_kosztow': "{:,.2f} zł".format(0),
                'realna_suma_kosztow': "{}".format(0)}]



        stopa_obj = Stopa(bank.stopy.wibor_moje)
        nadplata_obj = Nadplata(bank.nadplaty.getNadplaty())


        inflacja_list = bank.stopy.getInflacja()


        data_w =  data_pierwszej_raty - relativedelta(months=1)
        odsetki_start = self.nalicz_odsetki(self.K0, 4.23/100, self.dzien_start, data_w)



        saldo = self.K0
        dzien_ostatnia_platnosc = data_w
        odsetki_suma = odsetki_start

        Suma_Kosztow = 0
        Real_Suma_Kosztow = 0



        wykres_stopy_procentowe = []

        for i_splaty, dsplaty in enumerate(daty_splaty):




            krokSplaty = KrokSplaty(i_splaty+1)

            krokSplaty.data_splaty = dsplaty.strftime('%d/%m/%Y')
            krokSplaty.saldo_start = saldo



            zdarzenia = []
            zdarzenia.append(Zdarzenie(dzien_ostatnia_platnosc, stopa_obj.getStopa(dzien_ostatnia_platnosc), saldo))

            last_stopa = stopa_obj.getStopa(dzien_ostatnia_platnosc)

            wykres_stopy_procentowe.append(
                                    {'day': dsplaty.strftime('%d/%m/%Y'),
                                     'value': last_stopa}
            )


            k = 12
            L = (saldo*last_stopa)
            M = k*(1-pow(k/(k+last_stopa),360-i_splaty) )
            I =L/M

            #szukaj raty zaplaconej
            zwrot = [item for item in raty_pobrane if item["nr"] == krokSplaty.krok_nr]
            if zwrot:
                I = zwrot[0]['kwota']


            zdarzenia.append(Zdarzenie(dsplaty, 0,0))

            lista_zmian = stopa_obj.pomiedzy(dzien_ostatnia_platnosc,dsplaty)

            if lista_zmian:

                for lz in lista_zmian:

                    if lz['dzien'] in zdarzenia:
                        # get item
                        z = zdarzenia[zdarzenia.index(lz['dzien'])]
                        z.saldo = saldo
                        z.stopa = lz['stopa']


                    else:
                        print('dadane zdarzenies')
                        # add item
                        zdarzenia.append(Zdarzenie(lz['dzien'], lz['stopa'], saldo))
                        last_stopa = lz['stopa']

            lista_zmian_nadplaty = nadplata_obj.pomiedzy(dzien_ostatnia_platnosc,dsplaty)

            if lista_zmian_nadplaty:
                for lz in lista_zmian_nadplaty:
                    if lz['dzien'] in zdarzenia:
                        print('duplicate nadplata')
                        # get item
                        z = zdarzenia[zdarzenia.index(lz['dzien'])]
                        if lz['nr'] != 0 and lz['dzien']<self.dzien_start+relativedelta(years=3):
                            wartosc_nadplaty = lz['wartosc']
                            oplata =  0.01*lz['wartosc']


                        else:
                            wartosc_nadplaty = lz['wartosc']
                            oplata =  0

                        saldo = saldo - wartosc_nadplaty
                        krokSplaty.nadplaty += wartosc_nadplaty
                        krokSplaty.inne_oplaty += oplata

                        z.saldo = saldo
                        z.stopa = last_stopa

                    else:
                        print('dadane zdarzenies nadplata')
                        # add item
                        if lz['nr'] != 0 and lz['dzien']<self.dzien_start+relativedelta(years=3):
                            wartosc_nadplaty = lz['wartosc']
                            oplata =  0.01*lz['wartosc']


                        else:
                            wartosc_nadplaty = lz['wartosc']
                            oplata =  0


                        saldo = saldo - wartosc_nadplaty
                        krokSplaty.nadplaty += wartosc_nadplaty
                        krokSplaty.inne_oplaty += oplata

                        zdarzenia.append(Zdarzenie(lz['dzien'], last_stopa, saldo))




            zdarzenia = sorted(zdarzenia)


            odsetki_krok = 0
            for zdi in range(0,len(zdarzenia)-1):
                zd1 = zdarzenia[zdi]
                zd2 = zdarzenia[zdi+1]
                odsetki_krok += self.nalicz_odsetki(zd1.saldo, zd1.r, zd1.data, zd2.data)






            odsetki_suma += odsetki_krok


            odsetki_row_copy = odsetki_suma

            odsetki_suma = odsetki_suma - I

            krokSplaty.odsetki_krok = odsetki_krok
            krokSplaty.odsetki_narastajaco = odsetki_row_copy
            krokSplaty.rata = I



            kapital_splata = 0
            if odsetki_suma < 0:
                kapital_splata = -odsetki_suma
                odsetki_suma = 0


            saldo = saldo - kapital_splata

            krokSplaty.saldo_koniec = saldo
            krokSplaty.kapital_splata = kapital_splata



            krokSplaty.suma_kosztow = krokSplaty.inne_oplaty+krokSplaty.nadplaty+krokSplaty.rata
            nA = 6 - krokSplaty.krok_nr

            Suma_Kosztow += krokSplaty.suma_kosztow



            krokSplaty.realna_suma_kosztow = krokSplaty.suma_kosztow*pow(1+inflacja_list[krokSplaty.krok_nr-1]['value'], nA)

            Real_Suma_Kosztow += krokSplaty.realna_suma_kosztow





            rowx = {'nr': krokSplaty.krok_nr,
                    'data': krokSplaty.data_splaty,
                    'saldo_start': "{:,.2f} zł".format(krokSplaty.saldo_start),
                    'saldo_koniec': "{:,.2f} zł".format(krokSplaty.saldo_koniec),
                    'rata':  "{:,.2f} zł".format(krokSplaty.rata),
                    'kapital_splata': "{:,.2f} zł".format(krokSplaty.kapital_splata),
                    'odsetki':  "{:,.2f} zł".format(krokSplaty.odsetki_narastajaco),
                    'nadplaty':  "{:,.2f} zł".format(krokSplaty.nadplaty),
                    'inne_oplaty': "{:,.2f} zł".format(krokSplaty.inne_oplaty),
                    'suma_kosztow': "{:,.2f} zł".format(krokSplaty.suma_kosztow),
                    'realna_suma_kosztow': "{}".format(krokSplaty.realna_suma_kosztow)}

            result.append(rowx)








            dzien_ostatnia_platnosc = dsplaty

            if krokSplaty.saldo_koniec<=0:
                break




        return result, "{:,.2f} zł".format(Suma_Kosztow),  "{:,.2f} zł".format(Real_Suma_Kosztow), wykres_stopy_procentowe









class Kredyt:

    #def __new__(cls,  N, dzien_start, dzien_platnosci):
    #    return object.__new__(cls)

    def __init__(self, N, dzien_start, dzien_platnosci):
        """
        N - pożyczona kwota
        dzien start - dzień uruchomienia kredytu
        dzien platnosci - przesuwna
        """


        self.N = N
        self.dzien_start = datetime.datetime.strptime(dzien_start, "%d/%m/%Y")
        self.dzien_platnosci = datetime.datetime.strptime(dzien_platnosci, "%d/%m/%Y")


    def policz_kredyt(self):

        dni_odsetki_poczatkowe = (self.dzien_platnosci-self.dzien_start).days

        def dni_rok(day):

            rok = day.year

            return datetime.date(rok, 12, 31).timetuple().tm_yday

        stopa_obj = Stopa(bank.stopy.wibor_moje)
        stopa_dzien = stopa_obj.getStopa(self.dzien_platnosci) + 0.01
        print(stopa_dzien)

        dni_w_roku = dni_rok(self.dzien_platnosci)
        print(dni_w_roku)

        odsetki_poczatkowe = self.N * (stopa_dzien/dni_w_roku)*dni_odsetki_poczatkowe

        print("---odsetki poczatkowe---", odsetki_poczatkowe)

        K0 = 460000 + odsetki_poczatkowe









    def oblicz_roznice(self):
        """
        Co by było gdyby kredyt był nadpłacany?
        Obliczenie różnicy w dwóch wariantach.
        """

        dni_odsetki_poczatkowe = (datetime.datetime.strptime('18/12/2021', "%d/%m/%Y")-self.dzien_start).days


        r = 4.23/100
        N_od_banku = 460000

        odsetki_poczatkowe = N_od_banku*r*(dni_odsetki_poczatkowe/365)

        print(odsetki_poczatkowe)

        # poczatkowa kwota do splaty po uwzlednieniu opoznienia 1 raty
        N0 = N_od_banku + odsetki_poczatkowe

        N_i = N0
        N_i2 = N0

        I_suma = odsetki_poczatkowe
        I_suma2 = odsetki_poczatkowe


        stopa_procentowa = Stopa(bank.stopy.wibor_moje)

        #result_roznice = [ {'N1': N0, 'N2': N0} ]
        result_roznice = []

        #ile okresow (miesiecy) splaty kredytu
        n = 360
        for i_n in range(0,n):

            data_i = self.dzien_platnosci + relativedelta(months=i_n)

            r_i = stopa_procentowa.getStopa(data_i)

            r_i2 = r_i


            if 1 <= i_n < 12:
                r_i += 0.01


            I_i =  rata_rowna(N_i,r_i, n-i_n, 12)
            I_i2 = rata_rowna(N_i2,r_i2, n-i_n, 12)


            o_i = r_i/12*N_i
            o_i2 = r_i2/12*N_i2



            delta_I = I_i - I_i2


            N_i = N_i - (I_i - o_i)
            N_i2 = N_i2 - (I_i2 - o_i2) - delta_I

            I_suma = I_suma + I_i
            if N_i2>0:
                I_suma2 = I_suma2 + I_i2

            #print(data_i, r_i,  I_i, I_i2, delta_I)

            #result_roznice += {'N1': N_i, 'N2': N_i2}

            result_roznice.append({'N1': I_suma, 'N2': I_suma2})

        print(I_suma, I_suma2, I_suma-I_suma2)


        return result_roznice
