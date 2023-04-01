from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField, RadioField)
from wtforms.validators import InputRequired, Length




class KredytForm(FlaskForm):

    data_uruchomienia = StringField('data_uruchomienia', validators=[InputRequired(), Length(min=10, max=10)], description="DD/MM/YYYY")


