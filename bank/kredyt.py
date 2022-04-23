


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





class Kredyt:

    #def __new__(cls,  N, dzien_start, dzien_platnosci):
    #    return object.__new__(cls)

    def __init__(self, N, dzien_start, dzien_platnosci):
        # N - pożyczona kwota
        # dzien start - dzień uruchomienia kredytu
        # dzien platnosci - przesuwna


        self.N = N
        self.dzien_start = datetime.datetime.strptime(dzien_start, "%d/%m/%Y")
        self.dzien_platnosci = datetime.datetime.strptime(dzien_platnosci, "%d/%m/%Y")



    def oblicz_roznice(self):

        #print(self.dzien_start + relativedelta(months=4) )

        #dni = (self.dzien_platnosci-self.dzien_start).days

        dni = ( datetime.datetime.strptime('18/11/2021', "%d/%m/%Y")-self.dzien_start).days

        #print(dni)

        r = 4.23/100
        K = 460000

        o = K*r*(dni/365)

        # poczatkowa kwota do splaty po uwzlednieniu opoznienia 1 raty
        N0 = K + o

        n = 360

        stopa_dane = bank.stopy.wibor_moje

        stopa_df = pd.DataFrame(stopa_dane)
        stopa_df['day'] = pd.to_datetime(stopa_df['day'], format="%d/%m/%Y")
        stopa_df = stopa_df.sort_values(by="day")


        N_i = N0
        N_i2 = N0

        I_suma = o
        I_suma2 = o

        for i_n in range(0,n):

            data_i = self.dzien_platnosci + relativedelta(months=i_n+1)

            r_i = stopa_df[stopa_df['day']<=data_i]['value'].iloc[-1] / 100.0

            r_i2 = r_i


            if i_n>0 and i_n<12:
                r_i = r_i2+ 0.01


            I_i = rata_rowna(N_i,r_i, n-i_n, 12)
            I_i2 = rata_rowna(N_i2,r_i2, n-i_n, 12)







            o_i = r_i/12*N_i
            o_i2 = r_i2/12*N_i2



            delta_I = I_i - I_i2


            N_i = N_i - (I_i - o_i)

            N_i2 = N_i2 - (I_i2 - o_i2 + delta_I)

            I_suma = I_suma + I_i
            if N_i2>0:
                I_suma2 = I_suma2 + I_i2

            print(data_i, r_i,  I_i, I_i2, delta_I)


        print(I_suma, I_suma2, I_suma-I_suma2)

        #I,D = rata_rowna_prosta(K + o, 4.23/100, 360, 12)

        #print(o)
        #print(I)


        return bank.stopy.wibor_moje
