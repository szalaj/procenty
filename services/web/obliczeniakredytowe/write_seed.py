
# run with m switch from web/ $ python -m project.write_seed
from obliczeniakredytowe import init_app
import pandas as pd
from obliczeniakredytowe.models import Dom,User,InflacjaMM
import csv
import datetime
app = init_app()

from obliczeniakredytowe import db

def load_user():
    with app.app_context():
        with open('./obliczeniakredytowe/seeds/user.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                d = User(name=row[0])
                d.set_password(row[1])
                db.session.add(d)
                db.session.commit()
            
def load_dom():
    with app.app_context():
        with open('./obliczeniakredytowe/seeds/dom.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                d = Dom(wartosc=row[0], data_zakupu=row[1])
                db.session.add(d)
                db.session.commit()


def load_inflacja():
    with app.app_context():
        inflacja_df = pd.read_csv('obliczeniakredytowe/seeds/miesieczne_wskazniki_cen_towarow_i_uslug_konsumpcyjnych_od_1982_roku.csv', sep=';', encoding='cp1252')

        #inflacja_df = pd.read_csv('project/seeds/miesieczne_wskazniki_cen_towarow_i_uslug_konsumpcyjnych_od_1982_roku.csv', sep=';')
        
        inflacja_mm = inflacja_df[(inflacja_df['Sposob prezentacji']=='Poprzedni miesiac = 100') & (~inflacja_df['Wartosc'].isnull())]
        inflacja_mm['Wartosc'] = inflacja_mm['Wartosc'].astype("string")

        #print(inflacja_mm)
        for index, row in inflacja_mm.iterrows():
            data = f"{row['Rok']}-{row['Miesiac']:02d}"
            wartosc = float(row['Wartosc'].replace(',','.'))
            d = InflacjaMM(miesiac=datetime.datetime.strptime(data, '%Y-%m'), wartosc=wartosc)
            db.session.add(d)
            db.session.commit()

if __name__ == "__main__":
    print('ehlo')
    load_user()