


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



    def oblicz_roznice(self):
        """
        Co by było gdyby kredyt był nadpłacany?
        Obliczenie różnicy w dwóch wariantach.
        """

        dni_odsetki_poczatkowe = (datetime.datetime.strptime('18/11/2021', "%d/%m/%Y")-self.dzien_start).days


        r = 4.23/100
        N_od_banku = 460000

        odsetki_poczatkowe = N_od_banku*r*(dni_odsetki_poczatkowe/365)

        # poczatkowa kwota do splaty po uwzlednieniu opoznienia 1 raty
        N0 = N_od_banku + odsetki_poczatkowe



        N_i = N0
        N_i2 = N0

        I_suma = odsetki_poczatkowe
        I_suma2 = odsetki_poczatkowe


        stopa_procentowa = Stopa(bank.stopy.wibor_moje)

        result_roznice = [ {'N1': N0, 'N2': N0} ]

        #ile okresow (miesiecy) splaty kredytu
        n = 360
        for i_n in range(0,n):

            data_i = self.dzien_platnosci + relativedelta(months=i_n)

            r_i = stopa_procentowa.getStopa(data_i)

            r_i2 = r_i


            if 1 <= i_n < 12:
                r_i = r_i2 + 0.01


            I_i =  rata_rowna(N_i,r_i, n-i_n, 12)
            I_i2 = rata_rowna(N_i2,r_i2, n-i_n, 12)


            o_i = r_i/12*N_i
            o_i2 = r_i2/12*N_i2



            delta_I = I_i - I_i2


            N_i = N_i - (I_i - o_i)

            N_i2 = N_i2 - (I_i2 - o_i2 + delta_I)

            I_suma = I_suma + I_i
            if N_i2>0:
                I_suma2 = I_suma2 + I_i2

            #print(data_i, r_i,  I_i, I_i2, delta_I)

            result_roznice += {'N1': N_i, 'N2': N_i2}

        print(I_suma, I_suma2, I_suma-I_suma2)


        return result_roznice
