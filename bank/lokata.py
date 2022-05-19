
import datetime
from dateutil.relativedelta import relativedelta


class Lokata:

    def __init__(self, kwota, start_data, koniec_data, roczne_oprc):

        self.kwota = kwota
        self.r = roczne_oprc
        self.start_data =  datetime.datetime.strptime(start_data, "%d/%m/%Y")
        self.koniec_data = datetime.datetime.strptime(koniec_data, "%d/%m/%Y")

        self.saldo = {}

        liczba_miesiecy = (self.koniec_data.year - self.start_data.year) * 12 + self.koniec_data.month - self.start_data.month
        for i in range(1, liczba_miesiecy):
            data_next = self.start_data + relativedelta(months=i)

            self.saldo[data_next.strftime('%m/%Y')] = self.oblicz_kwote(data_next)


    def getSaldoMiesiac(self, miesiac):
        '''
        miesiac: mm/YYYY
        '''
        try:
            saldo = self.saldo[miesiac]
        except:
            saldo = 0

        return saldo



    def oblicz_kwote(self, dzien_obliczen):

        kwota_koniec = 0

        dni_odsetkowe = (dzien_obliczen-self.start_data).days

        lata_pelne = int(dni_odsetkowe/365)

        if lata_pelne>0:
            kwota_koniec = self.kwota*pow(1+self.r, lata_pelne)

            reszta_dni = dni_odsetkowe - lata_pelne*365

            odsetki_reszta = kwota_koniec * (self.r/365) * reszta_dni

            kwota_koniec += odsetki_reszta

        else:

            kwota_koniec = self.kwota

            odsetki_reszta = kwota_koniec * (self.r/365) * dni_odsetkowe

            kwota_koniec += odsetki_reszta





        return kwota_koniec
