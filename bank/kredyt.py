


import datetime
from dateutil.relativedelta import relativedelta



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


def rata_rowna(K0, r, N, k):
    pass


class Kredyt:

    def __init__(self, dzien_start, dzien_platnosci):

        # dzien start - dzień uruchomienia kredytu

        self.dzien_start = datetime.datetime.strptime(dzien_start, "%d/%m/%Y")
        self.dzien_platnosci = datetime.datetime.strptime(dzien_platnosci, "%d/%m/%Y")

        print(self.dzien_start + relativedelta(months=4) )


        dni = (self.dzien_platnosci-self.dzien_start).days

        dni = ( datetime.datetime.strptime('18/11/2021', "%d/%m/%Y")-self.dzien_start).days
        print(dni)
        r = 4.23/100
        K = 460000

        o = K*r*(dni/365)


        I,D = rata_rowna_prosta(K + o, 4.23/100, 360, 12)

        print(o)
        print(I)
