from flask_login import UserMixin
from .. import db
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

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
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)



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
    ubezpieczenie_pomostowe_do = db.Column(db.DateTime, nullable=True)
    ubezpieczenie_pomostowe_stopa = db.Column(db.Numeric(14,2), nullable=True)


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
                'marza': float(self.marza),
                'ubezpieczenie_pomostowe_do': dt.datetime.strftime(self.ubezpieczenie_pomostowe_do, '%Y-%m-%d') if self.ubezpieczenie_pomostowe_do else None,
                'ubezpieczenie_pomostowe_stopa': float(self.ubezpieczenie_pomostowe_stopa) if self.ubezpieczenie_pomostowe_stopa else None}


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
    


class Wibor(db.Model):
    __tablename__ = 'wibor'

    id = db.Column(db.Integer, primary_key=True) 
    rodzaj  = db.Column(db.String, nullable=False)
    data = db.Column(db.DateTime, nullable=False)
    wartosc = db.Column(db.Numeric(14,2), nullable=False)

    def __repr__(self):
        return f"{self.rodzaj} - {self.wartosc} - {self.data}"
    
    def as_dict(self):
       return {'id': self.id,
               'data': dt.datetime.strftime(self.data, '%Y-%m-%d'),
                'wartosc': float(self.wartosc),
                'rodzaj':self.rodzaj}
    


class Wakacje(db.Model):
    __tablename__ = 'wakacje'

    id = db.Column(db.Integer, primary_key=True) 
    kredyt_id  = db.Column(db.Integer, db.ForeignKey("kredyt.id"), nullable=False)
    miesiac = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"{self.kredyt_id} - {self.miesiac}"
    
    def as_dict(self):
       return {'id': self.id,
               'miesiac': dt.datetime.strftime(self.miesiac, '%Y-%m'),
               'kredyt_id':self.kredyt_id}
    
class DniSplaty(db.Model):
    __tablename__ = 'dni_splaty'

    id = db.Column(db.Integer, primary_key=True) 
    kredyt_id  = db.Column(db.Integer, db.ForeignKey("kredyt.id"), nullable=False)
    dzien_splaty = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"{self.kredyt_id} - {self.dzien_splaty}"
    
    def as_dict(self):
       return {'id': self.id,
               'dzien_splaty': dt.datetime.strftime(self.dzien_splaty, '%Y-%m-%d'),
               'kredyt_id':self.kredyt_id}