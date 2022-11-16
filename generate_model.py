import yaml
import sys
import getopt
import argparse
import datetime as dt
import time
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

        delta_d1 =  time.mktime(d1a.timetuple()) - time.mktime(d0.timetuple())
        delta_p1 = p1 - p0

        self.a1 = delta_p1/delta_d1
        self.b1 = p0 - d0*self.a1

        delta_d2 =  time.mktime(d2.timetuple()) - time.mktime(d1b.timetuple())
        delta_p2 = p2 - p1

        self.a2 = delta_p2/delta_d2
        self.b2 = p1 - d1b*self.a2

    def getOpr(self, dzien:dt.timestamp):


        if dzien >= self.d0 and dzien < self.d1a:
            dx = time.mktime(dzien.timetuple())
            return self.a1*dx + self.b1
        elif dzien >= self.d1a and dzien < self.d1b:
            return self.p1
        elif dzien >= self.d1b < self.d2:
            dx = time.mktime(dzien.timetuple())
            return self.a2*dx + self.b2
        elif dzien > self.d2:
            return self.p2
        else:
            raise Exception("dzien spoza przedzialu")

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

