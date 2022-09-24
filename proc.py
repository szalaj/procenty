import yaml
import sys
import getopt
import argparse
if __name__== "__main__":
    

    parser = argparse.ArgumentParser()
    parser.add_argument("echo")
    parser.add_argument("-v", "--verbosity", type=int,
                    help="increase output verbosity")
    args = parser.parse_args()
    print(args.echo)

    
    stream = open("./models/mod1.yml", 'r')
    dictionary = yaml.safe_load(stream)
    for key, value in dictionary.items():
        print (key + " : " + str(value))