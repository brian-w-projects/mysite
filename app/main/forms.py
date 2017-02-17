from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms import validators

class SearchForm(FlaskForm):
    search = StringField('Search Term: ')
    user = StringField('Search User: ')
    date = DateField('Search Date: ', format='%m/%d/%Y')
    submit = SubmitField('Submit')