import datetime
from dateutil.relativedelta import relativedelta
import math
from functools import reduce  # Required in Python 3
import operator

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



def prod(iterable):
    return reduce(operator.mul, iterable, 1)

def getInflacja():
    '''
    inflacja ustalana domyslnie rr, potem obliczana na mm
    '''

    inflacja_data = []
    data_start = datetime.datetime.strptime('04/10/2020', "%d/%m/%Y")

    #mm = 0.004
    #rr = pow(1+mm,12)-1

    mm_lista = []

    for i in range(0,580):
        data_next = data_start + relativedelta(months=i)

        #rr = m1 * m2 * m3.. * m12

        #rr/(m1z * m2z) = m3 * m4.. * m12


        rr = 0.08+0.01*math.sin(0.1*i)

        if i==0:
            mm = pow(1+rr,1/12)-1
            #mm_lista.append(mm)
        else:
            mm_znane = mm_lista[-11:]
            mm_dod = [x+1 for x in mm_znane]
            ile = len(mm_znane)
            if ile<=0:
                raise Excepttion('ale jaja')
            produkt = prod(mm_dod)
            mm = pow((1+rr)/(produkt), 1/(12-ile)) - 1

        mm_lista.append(mm)


        inflacja_data.append({'month': data_next.strftime('%m/%Y'),
                              'mm': mm,
                              'rr': rr})

    return inflacja_data


def getStopy(inflacja_dane):

    stopy = []

    for infl in inflacja_dane:

        day =  datetime.datetime.strptime('04/{}'.format(infl['month']), "%d/%m/%Y")
        stopa = infl['rr']*100 + 1

        stopy.append({'day': day.strftime('%d/%m/%Y'), 'value': stopa})

    return stopy
