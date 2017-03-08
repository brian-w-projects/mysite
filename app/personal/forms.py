from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms import validators

class ChangeForm(FlaskForm):
    about_me = TextAreaField('About Me: ', validators=[validators.Length(max=500)])
    password = PasswordField('Password: ', validators=[validators.Optional(), validators.EqualTo('password_confirm'), validators.Length(min=8)])
    password_confirm = PasswordField('Confirm: ', validators=[])
    updates = BooleanField('I would like to receive updates: ')
    limit = SelectField('Rec Display Amount: ', choices=[('10', '10'), ('20', '20'), ('50', '50')])
    submit = SubmitField('Update')

class PostForm(FlaskForm):
    title = StringField('Title: ', validators=[validators.DataRequired()])
    public = BooleanField('Public: ')
    text = TextAreaField('Rec: ', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')

class EditForm(FlaskForm):
    title = StringField('Title: ', validators=[validators.DataRequired()])
    public = BooleanField('Public: ')
    text = TextAreaField('Rec: ', validators=[validators.DataRequired()])
    delete = BooleanField('Delete: ', validators=[validators.EqualTo('delete_confirm')])
    delete_confirm = BooleanField('Delete Confirm: ')
    submit = SubmitField('Submit')
    
class CommentEditForm(FlaskForm):
    text = TextAreaField('Rec: ', validators=[validators.DataRequired()])
    delete = BooleanField('Delete: ')
    submit = SubmitField('Submit')