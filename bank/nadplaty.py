import datetime
from dateutil.relativedelta import relativedelta


def getNadplaty():

    nadplaty_moje = [
                    {'day': '25/04/2022', 'value': 3000},
                    {'day': '02/05/2022', 'value': 200},
                    {'day': '05/05/2022', 'value': 608}



                  ]

    # data_pierwszej_nadplaty = datetime.datetime.strptime('04/06/2022', "%d/%m/%Y")
    # for i in range(0,351):
    #     data_next = data_pierwszej_nadplaty + relativedelta(months=i)
    #     nadplaty_moje.append({'day': data_next.strftime('%d/%m/%Y'),
    #                             'value': 1000})

    for i,nadpl in enumerate(nadplaty_moje):
         nadpl['nr'] = i

    return nadplaty_moje
