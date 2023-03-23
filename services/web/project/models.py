from flask_login import UserMixin
from . import db
from sqlalchemy.sql import func


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
     created = db.DateTime()

     def __repr__(self):
         return f"<{self.user} - {self.created}>"



class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(1000))
    password = db.Column(db.String(100))


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
