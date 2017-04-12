from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField, SelectField, validators

class SearchForm(FlaskForm):
    type = SelectField('Search For: ', choices=[('Recs', 'Recs'), ('Comments', 'Comments')])
    search = StringField('Search Term: ')
    user = StringField('Search User: ')
    date = DateField('Search Date: ', format='%m/%d/%Y')
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    text = TextAreaField('Rec: ', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')