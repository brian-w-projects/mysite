from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms import validators

class VerifyForm(FlaskForm):
    privatize = BooleanField('Make Private: ')
    submit = SubmitField('Confirm Recs')