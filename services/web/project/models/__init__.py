from flask_login import UserMixin
from .. import db
from sqlalchemy.sql import func

import datetime as dt



class Dom(db.Model):
    __tablename__ = 'dom'
    id = db.Column(db.Integer, primary_key=True) # primardy keys are required by SQLAlchemy
    wartosc = db.Column(db.Numeric, nullable=False)
    data_zakupu = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<Dom {self.id}-{self.wartosc}-{self.data_zakupu}>"


class Zapytanie(db.Model):
     __tablename__ = 'zapytanie'
     id = db.Column(db.Integer, primary_key=True)
     user = db.Column(db.String(1000))
     created = db.Column(db.DateTime())

     def __repr__(self):
         return f"<{self.user} - {self.created}>"



class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(1000), unique=True)
    password = db.Column(db.String(100))

    def __repr__(self):
        return f"<{self.id} - {self.name}>"

    def to_json(self):        
        return {"nazwa": self.name}

    def is_authenticated(self):
        return True

    def is_active(self):   
        return True           

    def is_anonymous(self):
        return False          

    def get_id(self):         
        return self.id


class InflacjaMM(db.Model):
    __tablename__ = 'inflacjamm'

    id = db.Column(db.Integer, primary_key=True) 
    miesiac = db.Column(db.DateTime, unique=True, nullable=False)
    wartosc = db.Column(db.Numeric(4,2), nullable=False)

    def __repr__(self):
        return f"{self.miesiac}"


class Kredyt(db.Model):
    __tablename__ = 'kredyt'

    id = db.Column(db.Integer, primary_key=True) 
    uzytkownik = db.Column(db.String, nullable=False)
    data_uruchomienia = db.Column(db.DateTime, nullable=False)
    data_umowy = db.Column(db.DateTime, nullable=True)
    wartosc = db.Column(db.Numeric(14,2), nullable=False)
    okresy = db.Column(db.Integer, nullable=False)
    marza = db.Column(db.Float, nullable=False)
    rodzaj_wiboru = db.Column(db.String, nullable=False)
    rodzaj_rat = db.Column(db.String, nullable=False)


    def __repr__(self):
        return f"{self.data_uruchomienia} - {self.wartosc}"
    
    def as_dict(self):
       return {'id': self.id,
               'data_uruchomienia': dt.datetime.strftime(self.data_uruchomienia, '%Y-%m-%d'),
                'wartosc': float(self.wartosc),
                'uzytkownik':self.uzytkownik,
                'okresy':self.okresy,
                'rodzaj_wiboru':self.rodzaj_wiboru,
                'rodzaj_rat':self.rodzaj_rat,
                'marza': float(self.marza)}

class Nadplata(db.Model):
    __tablename__ = 'nadplata'

    id = db.Column(db.Integer, primary_key=True) 
    kredyt_id  = db.Column(db.Integer, db.ForeignKey("kredyt.id"), nullable=False)
    data_nadplaty = db.Column(db.DateTime, nullable=False)
    wartosc = db.Column(db.Numeric(14,2), nullable=False)

    def __repr__(self):
        return f"{self.kredyt_id} - {self.wartosc}"
    
    def as_dict(self):
       return {'id': self.id,
               'data_nadplaty': dt.datetime.strftime(self.data_nadplaty, '%Y-%m-%d'),
                'wartosc': float(self.wartosc),
                'kredyt_id':self.kredyt_id}