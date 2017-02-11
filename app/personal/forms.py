from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms import validators

class ChangeForm(FlaskForm):
    password = PasswordField('Password: ', validators=[validators.EqualTo('password_confirm')])
    password_confirm = PasswordField('Confirm: ', validators=[])
    updates = BooleanField('I would like to receive updates: ')
    submit = SubmitField('Update')