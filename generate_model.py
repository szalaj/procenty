import yaml
import sys
import getopt
import argparse
import datetime as dt
from dateutil.relativedelta import relativedelta
from collections import OrderedDict


class Oprocentowanie:

    def __init__(self, p0, p1, p2, d0, d1a, d1b, d2):

        # /
        # p - oprocentiowanie
        # d - data
        # (d0, p0) - start kredytu 
        # p1 - wysokosc maksymalna ()
        # d1a , d1b - czas trwania maks opr
        # d2, p2 - dojscie do oprocentowania stabilnego

        self.p0 = p0
        self.p1 = p1
        self.p2 = p2

        self.d0 = d0
        self.d1a = d1a
        self.d1b = d1b
        self.d2 = d2

    def getOpr(self, dzien:dt.timestamp):
        pass

def generate(plik, kapital, oprocentowanie, okresy, start_date):

    print(start_date)

    miesiace = [(start_date + relativedelta(months=i)).strftime('%Y-%m-%d') for i in range(okresy+1)]

    
    data = {"K": kapital,
            "p": oprocentowanie,
            "start": miesiace[0],
            "daty_splaty": miesiace[1:]}

    with open(plik, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False, sort_keys=False)

if __name__ == '__main__':

    try:

        opts, arg = getopt.getopt(sys.argv[1:], 'p:k:r:o:s:',  ["plik=", "kapital=", "oprocentowanie=", "okresy=", "startdate="])
        
       
        for opt, arg in opts:
            print("{} : {}".format(opt, arg))
            if opt in ("-o", "--okresy"):
                okresy = int(arg)
            if opt in ("-s", "--startdate"):
                start_date = dt.datetime.strptime(arg, '%Y-%m-%d')
            if opt in ("-p", "--plik"):
                plik = str(arg)
            if opt in ("-k", "--kapital"):
                kapital = float(arg)
            if opt in ("-r", "--oprocentowanie"):
                oprocentowanie = float(arg)
            
        generate(plik, kapital, oprocentowanie, okresy, start_date)
        
             
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

