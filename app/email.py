from flask import current_app, render_template
from . import mail
from flask_mail import Message
from .tasks import send_async_email

def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message('Confirm Account',
                  sender=app.config['MAIL_USERNAME'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    send_async_email(app, msg)