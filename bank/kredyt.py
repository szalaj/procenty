


import datetime
from dateutil.relativedelta import relativedelta

import bank.stopy

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



class Historia:

    def __init__(self):

        self.historia = []

    def dodaj(self, komunikat):

        pass



class StalaRata:


    def __init__(self, K0, N, r, dzien_start):



        self.K0 = K0
        self.N = N
        #self.dzien_uruchomienia =
        self.dzien_start = datetime.datetime.strptime(dzien_start, "%d/%m/%Y")


        self.r = r / 100.0


    def nalicz_odsetki(self, Kapital,  r_roczne, dzien_start, dzien_koniec):

        dni_odsetkowe = (dzien_koniec-dzien_start).days
        stopa_dzien = r_roczne / 365.0
        odsetki = Kapital * stopa_dzien * dni_odsetkowe

        return odsetki




    def policz(self):

        def wsp_a(k,rr):
            suma = 0
            for ki in range(k):
                suma += pow(1.0/(1.0+rr), ki+1)

            return suma


        k = 12
        L = (self.K0*self.r)
        M = k*(1-pow(k/(k+self.r),self.N) )

        I3 = self.K0/wsp_a(360, self.r/12.0)

        print('I3: ', I3)

        # rata rowna
        I2 = L/M

        print('I2: ', I2)


        I = 3077.24

        self.dzien_uruchomienia = datetime.datetime.strptime('04/11/2021', "%d/%m/%Y")
        Kn = self.K0


        S = 455437.06
        rs = 7.05/100.0

        ostatnia_rata = datetime.datetime.strptime('18/04/2022', "%d/%m/%Y")
        dzis = datetime.datetime.strptime('30/04/2022', "%d/%m/%Y")
        nadplata = datetime.datetime.strptime('25/04/2022', "%d/%m/%Y")

        d1 = datetime.datetime.strptime('18/10/2051', "%d/%m/%Y")
        d2 = datetime.datetime.strptime('04/11/2051', "%d/%m/%Y")



        od1 = self.nalicz_odsetki(S+3000, rs, ostatnia_rata, nadplata)
        od2 = self.nalicz_odsetki(S, rs, nadplata, dzis)



        od12 = self.nalicz_odsetki(2844.77,rs,  d1, d2)

        print('--od--', od1+od2)
        print('od12: ', od12)



        #odsetki = self.nalicz_odsetki(self.K0, self.r, self.dzien_start, self.dzien_uruchomienia)

        odsetki = 0

        dzien_ostatnia_platnosc = datetime.datetime.strptime('04/11/2021', "%d/%m/%Y")

        I = I2




        result = []

        daty_splaty = [self.dzien_start + relativedelta(months=n+1) for n in range(0, self.N)]

        daty_splaty[-1] =  datetime.datetime.strptime('04/11/2051', "%d/%m/%Y")

        for dsplaty in daty_splaty:



            dzien_platnosc = dsplaty

            odsetki += self.nalicz_odsetki(Kn, self.r, dzien_ostatnia_platnosc, dzien_platnosc)

            odsetki_krok = odsetki


            odsetki_reszta = odsetki - I
            kapital_splata = 0

            if odsetki_reszta < 0:
                kapital_splata = -odsetki_reszta
                Kn = Kn - kapital_splata

                odsetki = 0


            #Kn = Kn  - (I - odsetki)
            Kn = round(Kn,2)




            row = {'data': dzien_platnosc.strftime('%d/%m/%Y'),
                    'saldo': "{:,.2f} zł".format(Kn),
                    'rata':  "{:,.2f} zł".format(I),
                    'kapital_splata': "{:,.2f} zł".format(kapital_splata),
                    'odsetki':  "{:,.2f} zł".format(odsetki_krok)}

            result.append(row)

            dzien_ostatnia_platnosc = dzien_platnosc

        return Kn, result



    def policz2(self, data_rata):

        data_pierwszej_raty = datetime.datetime.strptime(data_rata, "%d/%m/%Y")

        daty_splaty = [data_pierwszej_raty + relativedelta(months=n) for n in range(0, self.N)]

        dane_df = [{'data': self.dzien_start,
                'saldo': self.K0,
                'rata':  0,
                'kapital_splata': 0,
                'odsetki':  0}]



        for dsplaty in daty_splaty:

            row = {'data': dsplaty,
                    'saldo': 0,
                    'rata':  0,
                    'kapital_splata': 0,
                    'odsetki':  0}

            dane_df.append(row)


        harmo_df = pd.DataFrame(dane_df)

        print(harmo_df)









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
