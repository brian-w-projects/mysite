from flask import render_template, session, redirect, url_for, request, abort, flash
from . import main
from .forms import SignUpForm
from .. import db
from ..models import Users
from flask_login import login_required, current_user
# from ..email import send_email
from ..decorators import admin_required, permission_required

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    form = SignUpForm(request.form)
    if request.method == 'POST':
        if form.validate():
            user = Users.query.filter_by(username=form.username.data).first()
            if user is None:
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('index.html'))
        else:
            print(form.errors)
            render_template('subscribe.html', form=form)
        
    return render_template('subscribe.html', form=form)