import json

import sys
import os
cwd = os.getcwd()
print(cwd)
sys.path.append(".") # Adds higher directory to python modules path
print(sys.path)
import bank.stopy as s
inflacja = s.getInflacja()

model = {'name': 'model1_inflacji', 'data': inflacja}

with open('./models/infl33.json', 'w') as f:
    json.dump(model, f)
