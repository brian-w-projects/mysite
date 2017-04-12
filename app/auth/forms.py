from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import BooleanField, PasswordField, StringField, SubmitField, validators

class LoginForm(FlaskForm):
    password = PasswordField('Password: ', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')
    username = StringField('Username: ', validators=[validators.DataRequired()])
    
class PasswordReset(FlaskForm):
    email = StringField('Email: ', validators=[validators.DataRequired(), validators.Email()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Send Email')
    username = StringField('Username: ', validators=[validators.DataRequired()])

class SignUpForm(FlaskForm):
    email = StringField('Email: ', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('Password: ', validators=[validators.DataRequired(), validators.EqualTo('password_confirm'), validators.Length(min=8)])
    password_confirm = PasswordField('Confirm: ', validators=[validators.DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Submit')
    token = StringField('Token: ', validators=[validators.DataRequired()])
    updates = BooleanField('I would like to receive updates: ')
    username = StringField('Username: ', validators=[validators.DataRequired(), validators.Length(min=5, max=12)])

class UsernameRecover(FlaskForm):
    email = StringField('Email: ', validators=[validators.DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Send Email')