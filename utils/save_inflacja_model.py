import json

import sys
sys.path.append("..") # Adds higher directory to python modules path

import bank.stopy as s
inflacja = s.getInflacja()

with open('../models/infl3.json', 'w') as f:
    json.dump(inflacja, f)
