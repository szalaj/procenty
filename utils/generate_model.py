import yaml
import sys
import getopt
import argparse
import datetime as dt
import time
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
import pandas as pd


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
        self.b1 = p0 - time.mktime(d0.timetuple())*self.a1

        delta_d2 =  time.mktime(d2.timetuple()) - time.mktime(d1b.timetuple())
        delta_p2 = p2 - p1

        self.a2 = delta_p2/delta_d2
        self.b2 = p1 - time.mktime(d1b.timetuple())*self.a2

    def getOpr(self, dzien:dt.datetime):

        if dzien >= self.d0 and dzien < self.d1a:
            dx = time.mktime(dzien.timetuple())
            return self.a1*dx + self.b1
        elif dzien >= self.d1a and dzien < self.d1b:
            return self.p1
        elif dzien >= self.d1b and dzien < self.d2:
            dx = time.mktime(dzien.timetuple())
            return self.a2*dx + self.b2
        elif dzien > self.d2:
            #print('wiecej')
            return self.p2
        else:
            raise Exception("dzien spoza przedzialu")

def generate(kapital, oprocentowanie, okresy, start_date, r_max, plik=None):


   

    miesiace = [(start_date + relativedelta(months=i)).strftime('%Y-%m-%d') for i in range(okresy+1)]

    opr = Oprocentowanie(oprocentowanie, r_max, 1, 
                                start_date,
                                dt.datetime.strptime('2025-04-02', '%Y-%m-%d'),
                                dt.datetime.strptime('2032-11-09', '%Y-%m-%d'),
                                dt.datetime.strptime('2038-04-02', '%Y-%m-%d') )

    
    opr_arr = []
    for i in range(0, int(okresy/3)+1):
       wibor_day =  start_date + relativedelta(months=3*i)
       wibor_value = opr.getOpr(wibor_day)

       opr_arr.append({"dzien":wibor_day.strftime('%Y-%m-%d'), "proc": wibor_value})

    data = {"K": kapital,
            "p": oprocentowanie,
            "start": miesiace[0],
            "daty_splaty": miesiace[1:],
            "oprocentowanie": opr_arr}
    if plik:
        with open('./models/{}'.format(plik), 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, sort_keys=False)
    
    return data


def generateFromWiborFile():

    df = pd.read_csv('static\plopln3m_d.csv', usecols=[0,1], index_col=0)
    print(df)


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
