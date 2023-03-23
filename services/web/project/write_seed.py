
# run with m switch from web/ $ python -m project.write_seed
from . import init_app

from project.models import Dom,User
import csv
app = init_app()

from project import db

if __name__ == "__main__":
    print('ehlo')
    with app.app_context():
        with open('./project/seeds/user.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                d = User(name=row[0], password=row[1])
                db.session.add(d)
                db.session.commit()