import yaml
import sys
import getopt
import argparse
import datetime as dt

if __name__== "__main__":

    stream = open("./models/mod1.yml", 'r')
    dane = yaml.safe_load(stream)
    for key, value in dane.items():
        print (key + " : " + str(value))

    k = 12
    p = dane['p']/100.0
    S = dane['K']
    N = dane['N']

    L = (S*p)
    M = k*(1-pow(k/(k+p), N))
    I = L/M

    print('I : {}'.format(I))