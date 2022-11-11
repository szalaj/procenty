import yaml
import sys
import getopt
import argparse
import datetime as dt
from dateutil.relativedelta import relativedelta
from collections import OrderedDict

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

