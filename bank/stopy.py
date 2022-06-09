import datetime
from dateutil.relativedelta import relativedelta
import math
wibor_moje = [
                {'day': '04/11/2021', 'value': 4.23},
                {'day': '04/02/2022', 'value': 7.05},
                {'day': '04/05/2022', 'value': 10.04},
                {'day': '04/08/2022', 'value': 13.04},
                {'day': '04/11/2022', 'value': 16.04},
                {'day': '04/11/2025', 'value': 14.04},
                {'day': '04/11/2027', 'value': 7.04},
                {'day': '04/11/2047', 'value': 16.04}
              ]

def getInflacja():

    inflacja_mm = []

    data_start = datetime.datetime.strptime('04/11/2021', "%d/%m/%Y")
    for i in range(0,360):
        data_next = data_start + relativedelta(months=i)
        inflacja_mm.append({'nr': i,
                            'day': data_next.strftime('%d/%m/%Y'),
                            'value': 0.005 + 0.001*math.sin(i)})



    return inflacja_mm

def getInflacja2():

    #inflacja_mm = []
    inflacja_mm ={}

    data_start = datetime.datetime.strptime('04/10/2020', "%d/%m/%Y")
    for i in range(0,580):
        data_next = data_start + relativedelta(months=i)

        # inflacja_mm.append({'nr': i,
        #                     'day': data_next.strftime('%m/%Y'),
        #                     'value': 0.01})

        inflacja_mm[data_next.strftime('%m/%Y')] = 0.002

    return inflacja_mm

def getInflacja3():


    inflacja_data = []

    data_start = datetime.datetime.strptime('04/10/2020', "%d/%m/%Y")

    mm = 0.004
    rr = pow(1+mm,12)-1

    for i in range(0,580):
        data_next = data_start + relativedelta(months=i)

        inflacja_data.append({'month': data_next.strftime('%m/%Y'),
                              'mm': mm,
                              'rr': rr})

    return inflacja_data
