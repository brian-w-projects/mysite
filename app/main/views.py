from flask import render_template, session, redirect, url_for, request, abort, flash
from . import main
from .forms import SignUpForm
from .. import db
from ..models import Users
from flask_login import login_required, current_user
# from ..email import send_email
from ..decorators import admin_required, permission_required
from ..email import send_email

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    form = SignUpForm(request.form)
    if request.method == 'POST' and form.validate():
        check_user = Users.query.filter_by(username=form.username.data).first()
        if check_user is None:
            user = Users(username=form.username.data, email=form.email.data, password=form.password.data, updates=form.updates.data)
            db.session.add(user)
            db.session.commit()
            token=user.generate_confirmation_token()
            send_email(form.email.data, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
            return redirect(url_for('.index'))
    return render_template('subscribe.html', form=form)