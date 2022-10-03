import yaml
import sys
import getopt
import argparse
if __name__== "__main__":

    stream = open("./models/mod1.yml", 'r')
    dane = yaml.safe_load(stream)
    for key, value in dane.items():
        print (key + " : " + str(value))

    k = 12
    p = dane['p']/100.0
    S = dane['K']
    L = (S*p)
    M = k*(1-pow(k/(k+p),360))
    I = L/M

    print('I : {}'.format(I))