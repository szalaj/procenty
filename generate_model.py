
import yaml
import sys
import getopt
import argparse
import datetime as dt

def generate(plik, okresy, start_date):

    print(start_date)

if __name__ == '__main__':

    try:

        opts, arg = getopt.getopt(sys.argv[1:], 'p:n:s:',  ["plik=", "okresy=", "startdate="])
        
       
        for opt, arg in opts:
            print("{} : {}".format(opt, arg))
            if opt in ("-n", "--okresy"):
                okresy = int(arg)
            if opt in ("-s", "--startdate"):
                start_date = dt.datetime.strptime(arg, '%Y-%m-%d')
            if opt in ("-p", "--plik"):
                plik = str(arg)
            
        generate(plik, okresy, start_date)
        
             
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

