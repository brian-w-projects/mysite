from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField, SelectField, validators

class SearchForm(FlaskForm):
    date = DateField('Search Date: ', format='%m/%d/%Y')
    search = StringField('Search Term: ')
    submit = SubmitField('Submit')
    type = SelectField('Search For: ', choices=[('Recs', 'Recs'), ('Comments', 'Comments')])
    user = StringField('Search User: ')

class CommentForm(FlaskForm):
    submit = SubmitField('Submit')
    text = TextAreaField('Rec: ', validators=[validators.DataRequired()])