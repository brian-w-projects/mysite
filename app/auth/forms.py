from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms import validators

class SignUpForm(FlaskForm):
    username = StringField('Username: ', validators=[validators.DataRequired(), validators.Length(min=4)])
    email = StringField('Email: ', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('Password: ', validators=[validators.DataRequired(), validators.EqualTo('password_confirm'), validators.Length(min=8)])
    password_confirm = PasswordField('Confirm: ', validators=[validators.DataRequired()])
    updates = BooleanField('I would like to receive updates: ')
    token = StringField('Token: ', validators=[validators.DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('Username: ', validators=[validators.DataRequired()])
    password = PasswordField('Password: ', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')
    
class PasswordReset(FlaskForm):
    username = StringField('Username: ', validators=[validators.DataRequired()])
    email = StringField('Email: ', validators=[validators.DataRequired(), validators.Email()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Send Email')
    
class UsernameRecover(FlaskForm):
    email = StringField('Email: ', validators=[validators.DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Send Email')