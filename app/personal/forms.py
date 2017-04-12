from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField, TextAreaField, validators

class ChangeForm(FlaskForm):
    about_me = TextAreaField('About Me: ', validators=[validators.Length(max=500)])
    password = PasswordField('Password: ', validators=[validators.Optional(), validators.EqualTo('password_confirm'), validators.Length(min=8)])
    password_confirm = PasswordField('Confirm: ', validators=[])
    updates = BooleanField('I would like to receive updates: ')
    limit = SelectField('Rec Display Amount: ', choices=[('10', '10'), ('20', '20'), ('50', '50')])
    submit = SubmitField('Update')

class CommentEditForm(FlaskForm):
    submit = SubmitField('Submit')
    text = TextAreaField('Rec: ', validators=[validators.DataRequired()])
    
class DeleteForm(FlaskForm):
    delete = BooleanField('Delete Comment: ', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')

class EditForm(FlaskForm):
    delete = BooleanField('Delete: ', validators=[validators.EqualTo('delete_confirm')])
    delete_confirm = BooleanField('Delete Confirm: ')
    title = StringField('Title: ', validators=[validators.DataRequired()])
    public = BooleanField('Public: ')
    submit = SubmitField('Submit')
    text = TextAreaField('Rec: ', validators=[validators.DataRequired()])

class PostForm(FlaskForm):
    public = BooleanField('Public: ')
    submit = SubmitField('Submit')
    text = TextAreaField('Rec: ', validators=[validators.DataRequired()])
    title = StringField('Title: ', validators=[validators.DataRequired()])