from flask_login import UserMixin

class User(UserMixin):   


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

