
- czasami trzeba zdef znowu 
$ export FLASK_APP=project/__init__.py


---------------------

$ flask shell
$ from project import db

- skasuj tablee jedengo modelu
User.__table__.drop(db.engine)

InflacjaMM.__table__.drop(db.engine)

- skasuj wszystko
db.drop_all()

-stworz wszystko
db.create_all()