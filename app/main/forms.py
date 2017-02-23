from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField, BooleanField
from wtforms import validators

class SearchForm(FlaskForm):
    search = StringField('Search Term: ')
    user = StringField('Search User: ')
    date = DateField('Search Date: ', format='%m/%d/%Y')
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    text = TextAreaField('Rec: ', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')

class DeleteForm(FlaskForm):
    delete = BooleanField('Delete: ', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')

class CommentEditForm(FlaskForm):
    text = TextAreaField('Rec: ', validators=[validators.DataRequired()])
    delete = BooleanField('Delete: ')
    submit = SubmitField('Submit')