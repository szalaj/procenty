
# run with m switch from web/ $ python -m project.write_seed
from project import init_app
import pandas as pd
from project.models import Dom,User,InflacjaMM
import csv
import datetime
app = init_app()

from project import db

def load_user():
    with app.app_context():
        with open('./project/seeds/user.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                d = User(name=row[0], password=row[1])
                db.session.add(d)
                db.session.commit()
            
def load_dom():
    with app.app_context():
        with open('./project/seeds/dom.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                d = Dom(wartosc=row[0], data_zakupu=row[1])
                db.session.add(d)
                db.session.commit()


def load_inflacja():
    with app.app_context():
        inflacja_df = pd.read_csv('project/seeds/miesieczne_wskazniki_cen_towarow_i_uslug_konsumpcyjnych_od_1982_roku.csv', sep=';', encoding='mbcs')

        
        
        inflacja_mm = inflacja_df[(inflacja_df['Sposób prezentacji']=='Poprzedni miesiąc = 100') & (~inflacja_df['Wartość'].isnull())]
        inflacja_mm['Wartość'] = inflacja_mm['Wartość'].astype("string")

        #print(inflacja_mm)
        for index, row in inflacja_mm.iterrows():
            data = f"{row['Rok']}-{row['Miesiąc']:02d}"
            wartosc = float(row['Wartość'].replace(',','.'))
            d = InflacjaMM(miesiac=datetime.datetime.strptime(data, '%Y-%m'), wartosc=wartosc)
            db.session.add(d)
            db.session.commit()

if __name__ == "__main__":
    print('ehlo')
    load_user()