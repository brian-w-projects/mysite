from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms import validators

class ChangeForm(FlaskForm):
    about_me = TextAreaField('About Me: ')
    password = PasswordField('Password: ', validators=[validators.EqualTo('password_confirm')])
    password_confirm = PasswordField('Confirm: ', validators=[])
    updates = BooleanField('I would like to receive updates: ')
    limit = SelectField('Rec Display Amount: ', choices=[('', ''), ('10', '10'), ('20', '20'), ('50', '50')])
    submit = SubmitField('Update')

class PostForm(FlaskForm):
    title = StringField('Title: ', validators=[validators.DataRequired()])
    public = BooleanField('Public: ')
    text = TextAreaField('Rec: ', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')

class EditForm(FlaskForm):
    title = StringField('TItle: ', validators=[validators.DataRequired()])
    public = BooleanField('Public: ')
    text = TextAreaField('Rec: ', validators=[validators.DataRequired()])
    delete = BooleanField('Delete: ', validators=[validators.EqualTo('delete_confirm')])
    delete_confirm = BooleanField('Delete Confirm: ')
    submit = SubmitField('Submit')
    