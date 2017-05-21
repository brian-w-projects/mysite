from flask import current_app, render_template
from . import mail
from flask_mail import Message
from .tasks import send_async_email
import sendgrid
import os
from sendgrid.helpers.mail import *

def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(app.config['MAIL_USERNAME'])
    to_email = Email(to)
    subject = "Confirm Account"
    content = Content('text/plain', render_template(template + '.txt', **kwargs))
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())