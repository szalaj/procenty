from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):

    id = db.Column(db.String(100), primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


    def __init__(self, nazwa):
        self.id = nazwa             

    def to_json(self):        
        return {"nazwa": self.nazwa}

    def is_authenticated(self):
        return True

    def is_active(self):   
        return True           

    def is_anonymous(self):
        return False          

    def get_id(self):         
        return str(self.id)

